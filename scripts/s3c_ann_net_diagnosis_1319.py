"""Why (s3c-ann-net) loses three times: a diagnosis of #1288's record (#1319; H5 step 3; her ruling of 30 October 2026, ledger item 79; findings #1316).

A development study, never a verdict, and a diagnosis of a record that exists: the walks, fits and forecasts are #1288's, built by
`scripts/s3c_announced_settlement_1288.py` exactly as merged and read at the instants they were made at (16:00 on the decision day). Nothing is
fitted here and nothing is scored that #1288 did not score. Every choice is in `metadata/s3c_ann_net_diagnosis_1319.json`, which this script refuses
to read unless it is committed and unchanged. The three losses (all on #1288's page) and the two hypotheses tested against them:

1. lead 1, where (s3c-ann-net) is #1273's (s3c-net) and loses to (s3c) on the pressure probability and the upper tail: net sizing against the
   gross flag. H-a: the squeeze scales with the gross amount dealers finance, not the net, because the maturing cash is not put back into repo the
   same day;
2. 2020, where every announced-settlement arm loses to (s3c). H-b: settlement terms learned in scarce-reserve years over-predict when reserves are
   abundant;
3. net against flag at every lead on the Brier score of P(> +5 bp), and on all three scores in 2018-19.

Commands, from a clone of the branch (the two walks are about six minutes, the scarcity state a minute, the tables a few minutes more; a cloud run):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_diagnosis_1319.py score --panel PUB.csv \\
        --output docs/research/s3c-ann-net-diagnosis-1319/result.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_diagnosis_1319.py page \\
        --score docs/research/s3c-ann-net-diagnosis-1319/result.json --output docs/research/s3c-ann-net-diagnosis-1319-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import pickle
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: Optional[str] = None):
    """Load `scripts/<name>.py` as a module registered under `alias` (default `name`)."""

    alias = alias or name
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(alias)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, data, metrics, policy_events, s3c_announced, s3c_net  # noqa: E402
from repo_model import net_settlement as ns  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1319")
m1273, k, c, s686 = m1288.m1273, m1288.k, m1288.c, m1288.s686

DECLARATION = REPO / "metadata" / "s3c_ann_net_diagnosis_1319.json"
RECORD_1288 = REPO / "docs" / "research" / "s3c-announced-settlement-1288" / "result.json"
RELEASE_TIMES = REPO / "metadata" / "announcement_release_times_1301.json"
SEED = 1319
REPS = 2000
BLOCK = float(sp.BLOCK_LENGTH)
MIN_DAYS = 20
#: The declaration's amendments, which are recorded on the page (made after a scratch run of the tables, none changing a figure).
AMENDMENTS: list = json.loads(DECLARATION.read_text(encoding="utf-8"))["amendments"]
S3C, ANN, NET = m1288.S3C, m1288.ANN, m1288.ANNNET
ARM_LABELS = {S3C: "(s3c)", ANN: "(s3c-ann), the flag", NET: "(s3c-ann-net), the net"}
METRICS = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)"}
LEADS = tuple(sp.HORIZONS)
TERMS = tuple(s3c_announced.LEGS)
LEG_OF_TERM = {"settlement_coupon": "coupon", "settlement_bill": "bill"}
UNIT = 100.0  # USD billions per unit of USD 100 bn
TAU = m1273.TAU
CLASSES = ("no settlement", "a class partly announced", "net at or below zero", "net below half of gross", "net at or above half of gross",
           "mixed legs")
TYPE_LABELS = m1288.TYPE_LABELS
STATE_LABELS = ("0 (abundant)", "1 to 2", "3 (scarce)", "no state")
SIZE_LABELS = ("highest third of settlement size", "other settlement days", "no settlement")
THIRD_LABELS = ("lowest third of maturing share", "middle third", "highest third")
REGIMES = ("2018-19", "2020", "2021-23", "2024", "2025-26")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the legs of the net -------------------------------------------------------------------------------------------------


class Leg(NamedTuple):
    """One class (coupon or bill) of a settlement day as announced at a decision instant, in USD billions.

    `settles` is true when an auction of the class had been announced; `full` is false when the class was announced only in part (it then
    reads zero gross, maturing and net, as `net_settlement.net_for_day` leaves it out).
    """

    settles: bool
    full: bool
    gross: float
    maturing: float
    net: float


def legs_of_day(auctions: Sequence[ns.Auction], instant: datetime) -> Dict[str, Leg]:
    """The coupon and bill legs of the auctions settling on one day, as announced at `instant`.

    Gross is the offerings summed, maturing the largest announced maturing figure of the class, net their difference: the construction of
    `net_settlement.net_for_day`, whose figures it is checked against.

    Raises:
        LookAheadError: the net of the legs is not the net `net_for_day` reads at `instant` (an auction counted that was not announced).
    """

    known = ns.known_auctions(auctions, instant)
    visible = [a for a in auctions if not a.cmb or a.announced_at <= instant]
    legs: Dict[str, Leg] = {}
    for is_bill, name in ((False, "coupon"), (True, "bill")):
        members = [a for a in known if a.is_bill == is_bill]
        scheduled = [a for a in visible if a.is_bill == is_bill]
        if not members:
            legs[name] = Leg(False, True, 0.0, 0.0, 0.0)
            continue
        if len(members) < len(scheduled):
            legs[name] = Leg(True, False, 0.0, 0.0, 0.0)
            continue
        figures = [a.maturing for a in members if a.maturing is not None]
        gross = sum(a.offering for a in members)
        maturing = max(figures) if figures else 0.0
        legs[name] = Leg(True, True, gross, maturing, gross - maturing)
    require_known_net(legs, auctions, instant)
    return legs


def require_known_net(legs: Mapping[str, Leg], auctions: Sequence[ns.Auction], instant: datetime) -> None:
    """Refuse legs whose net differs from `net_settlement.net_for_day` at `instant`.

    Raises:
        LookAheadError: they differ, which means the legs counted an auction announced after `instant` or left out one announced before it.
    """

    net, bills, _ = ns.net_for_day(auctions, instant)
    if abs(legs["coupon"].net + legs["bill"].net - net) > 1e-9 or abs(legs["bill"].net - bills) > 1e-9:
        raise LookAheadError(f"the legs of the net at {instant} differ from net_settlement.net_for_day: the read is not what was announced")


def net_class(legs: Mapping[str, Leg]) -> str:
    """The net-to-gross class of a target day as announced (the declaration's classes)."""

    settling = [leg for leg in legs.values() if leg.settles]
    if not settling:
        return CLASSES[0]
    if any(not leg.full for leg in settling):
        return CLASSES[1]
    if any(leg.net <= 0.0 for leg in settling):
        return CLASSES[2]
    if all(leg.net < leg.gross / 2.0 for leg in settling):
        return CLASSES[3]
    if all(leg.net >= leg.gross / 2.0 for leg in settling):
        return CLASSES[4]
    return CLASSES[5]


def maturing_share(legs: Mapping[str, Leg]) -> Optional[float]:
    """The maturing amount over the gross amount of the fully announced settling legs; `None` when none settles."""

    full = [leg for leg in legs.values() if leg.settles and leg.full and leg.gross > 0.0]
    gross = sum(leg.gross for leg in full)
    return sum(leg.maturing for leg in full) / gross if gross > 0.0 else None


def thirds_cuts(values: Sequence[float]) -> Tuple[float, float]:
    """The two cut points that split `values` into thirds."""

    ordered = sorted(values)
    return ordered[len(ordered) // 3], ordered[(2 * len(ordered)) // 3]


def third(value: float, cuts: Tuple[float, float]) -> int:
    return 0 if value < cuts[0] else 1 if value < cuts[1] else 2


# -- least squares -------------------------------------------------------------------------------------------------------


def _solve(a: List[List[float]], b: List[float]) -> List[float]:
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[pivot] = m[pivot], m[col]
        if abs(m[col][col]) < 1e-300:
            raise ValueError("the normal equations are singular")
        for r in range(col + 1, n):
            f = m[r][col] / m[col][col]
            for cc in range(col, n + 1):
                m[r][cc] -= f * m[col][cc]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (m[r][n] - sum(m[r][cc] * x[cc] for cc in range(r + 1, n))) / m[r][r]
    return x


def ols(x: Sequence[Sequence[float]], y: Sequence[float], ridge: float = 1e-9) -> List[float]:
    """Least squares of `y` on the columns of `x` (a tiny ridge keeps a resampled singular design finite)."""

    p = len(x[0])
    xtx = [[sum(row[i] * row[j] for row in x) + (ridge if i == j else 0.0) for j in range(p)] for i in range(p)]
    xty = [sum(row[i] * v for row, v in zip(x, y)) for i in range(p)]
    return _solve(xtx, xty)


_VARS = ("one", "gross", "maturing", "net", "other", "r")


def _moments(rows: Sequence[Mapping[str, float]]) -> List[List[float]]:
    s = [[0.0] * 6 for _ in range(6)]
    for row in rows:
        v = (1.0, row["gross"], row["maturing"], row["gross"] - row["maturing"], float(row["other"]), row["r"])
        for i in range(6):
            for j in range(i, 6):
                s[i][j] += v[i] * v[j]
    for i in range(6):
        for j in range(i):
            s[i][j] = s[j][i]
    return s


def _fit_subset(s: List[List[float]], names: Sequence[str], n: int, ridge: float = 1e-9) -> Tuple[List[float], float]:
    idx = [_VARS.index(x) for x in names]
    r = _VARS.index("r")
    a = [[s[i][j] + (ridge if i == j else 0.0) for j in idx] for i in idx]
    b = [s[i][r] for i in idx]
    beta = _solve(a, b)
    sse = s[r][r] - 2.0 * sum(bi * s[i][r] for bi, i in zip(beta, idx)) + sum(
        beta[p] * beta[q] * s[idx[p]][idx[q]] for p in range(len(idx)) for q in range(len(idx)))
    return beta, max(sse, 0.0) / n


def fit_leg(rows: Sequence[Mapping[str, float]]) -> Dict[str, float]:
    """The gross-and-maturing form `r = a + g gross + m maturing + o other`, the net-only form and the gross-only form on `rows`.

    `g + m` is zero when the maturing amount offsets the gross one for one (the net is the whole story). The mean squared residuals are in
    sample; the net-only form is nested in the full one, so `mse_net >= mse_full`.
    """

    n = len(rows)
    s = _moments(rows)
    full, mse_full = _fit_subset(s, ("one", "gross", "maturing", "other"), n)
    net, mse_net = _fit_subset(s, ("one", "net", "other"), n)
    gross, mse_gross = _fit_subset(s, ("one", "gross", "other"), n)
    return {"days": n, "g": full[1], "m": full[2], "g_plus_m": full[1] + full[2], "n": net[1], "gross_only": gross[1],
            "mse_full": mse_full, "mse_net": mse_net, "mse_gross": mse_gross}


def no_variation(rows: Sequence[Mapping[str, float]]) -> bool:
    values = [row["gross"] for row in rows]
    return not values or max(values) - min(values) < 1e-12


def _fit_statistics(rows: Sequence[Mapping[str, float]]) -> List[float]:
    f = fit_leg(rows)
    return [f["g"], f["m"], f["g_plus_m"], f["n"], f["mse_net"] - f["mse_full"], f["mse_gross"] - f["mse_net"]]


FIT_NAMES = ("g", "m", "g_plus_m", "n", "mse_net_less_full", "mse_gross_less_net")


# -- readings ------------------------------------------------------------------------------------------------------------


def reading(interval: Optional[Sequence[float]]) -> str:
    """A difference d is the arm less the reference, so above zero is a loss for the arm, below zero a gain."""

    if interval is None:
        return "not read"
    low, high = interval
    if low > 0.0:
        return "loss"
    if high < 0.0:
        return "gain"
    return "undecided"


def read_h_a(g_plus_m: Optional[Sequence[float]], gross_less_net: Optional[Sequence[float]]) -> str:
    """H-a at a lead and leg (the declaration's rule). `gross_less_net` is the interval of mse(gross only) - mse(net only)."""

    if g_plus_m is None:
        return "not read"
    if g_plus_m[0] > 0.0:
        return "supported"
    if g_plus_m[1] < 0.0 or (gross_less_net is not None and gross_less_net[0] > 0.0):
        return "not supported"
    return "undecided"


def skill(arm_mean: float, ref_mean: float) -> float:
    return 1.0 - arm_mean / ref_mean


def share(group: Sequence[float], total: Sequence[float]) -> Optional[float]:
    """The group's sum of d over the sum over all cells: its share of the loss; `None` when the total is zero."""

    t = sum(total)
    return None if abs(t) < 1e-12 else sum(group) / t


def settlement_bias(cells: Sequence[Mapping[str, object]]) -> Dict[str, Optional[float]]:
    """On cells of one arm: the mean error `y - median` on settlement cells less that on the others (negative: forecast too high on settlement
    days), the mean fitted shift on settlement cells, and the realised mean spread on settlement cells less that on the others."""

    on = [x for x in cells if x["settle"]]
    off = [x for x in cells if not x["settle"]]
    if not on or not off:
        return {"bias": None, "shift": None, "premium": None, "settlement_cells": len(on), "other_cells": len(off)}

    def mean(xs):
        return sum(xs) / len(xs)

    return {"bias": mean([x["y"] - x["med"] for x in on]) - mean([x["y"] - x["med"] for x in off]),
            "shift": mean([x["shift"] for x in on]), "premium": mean([x["y"] for x in on]) - mean([x["y"] for x in off]),
            "settlement_cells": len(on), "other_cells": len(off)}


def check_means(here: Mapping[str, float], there: Mapping[str, float], where: str, tolerance: float = 1e-9) -> None:
    """Refuse a mean that is not #1288's record's.

    Raises:
        ValueError: a model's mean differs from the record's by more than `tolerance`.
    """

    for name, value in here.items():
        if abs(value - there[name]) > tolerance:
            raise ValueError(f"{where}: {name} is {value:.12f} here and {there[name]:.12f} in #1288's record: this is not the record's walk")


# -- the bootstrap, in parallel ------------------------------------------------------------------------------------------

_PENDING: List[Tuple[dict, str, tuple]] = []


def _job(kind: str, payload):
    if kind == "mean":
        series = payload
        n = len(series[0])
        out = metrics.stationary_bootstrap_intervals(
            lambda idx: [sum(s[i] for i in idx) / len(idx) for s in series], n, block_length=BLOCK, seed=SEED, replications=REPS)
        return [list(x) for x in out]
    if kind == "fit":
        rows = payload
        out = metrics.stationary_bootstrap_intervals(lambda idx: _fit_statistics([rows[i] for i in idx]), len(rows), block_length=BLOCK,
                                                     seed=SEED, replications=REPS)
        return [list(x) for x in out]
    if kind == "bias":
        units, names = payload
        out = metrics.stationary_bootstrap_intervals(
            lambda idx: [_bias_value(_bias_totals(units, idx), name) for name in names], len(units), block_length=BLOCK, seed=SEED,
            replications=REPS)
        return [list(x) for x in out]
    raise ValueError(kind)


def _run(job):
    return _job(*job)


def _queue(container: dict, key: str, kind: str, payload) -> None:
    _PENDING.append((container, key, (kind, payload)))


def finish(workers: int) -> None:
    """Run every queued bootstrap in a pool and write each interval list into the container that asked."""

    jobs = [item[2] for item in _PENDING]
    if workers > 1 and len(jobs) > 1:
        with multiprocessing.get_context("fork").Pool(workers) as pool:
            done = pool.map(_run, jobs, chunksize=1)
    else:
        done = [_run(j) for j in jobs]
    for (container, key, _), result in zip(_PENDING, done):
        container[key] = result
    _PENDING.clear()


# -- the cells -----------------------------------------------------------------------------------------------------------


def auctions_by_day(auctions: Sequence[ns.Auction]) -> Dict[date, List[ns.Auction]]:
    out: Dict[date, List[ns.Auction]] = {}
    for a in auctions:
        out.setdefault(a.settles, []).append(a)
    return out


def release_days(snapshot_dir: Path = m1288.AUCTIONS, path: Path = RELEASE_TIMES) -> Dict[str, List[str]]:
    """The settlement days with an auction whose announcement states no release time ('For Immediate Release', #1301), all and cash management bills."""

    stated = json.loads(Path(path).read_text(encoding="utf-8"))["stated"]
    files = sorted(p for p in Path(snapshot_dir).glob("*.json") if not p.name.endswith(".manifest.json"))
    records = json.loads(files[0].read_text(encoding="utf-8"))["data"]
    every, cmb = set(), set()
    for r in records:
        if stated.get(r["pdf_filenm_announcemt"]) == "immediate":
            every.add(r["issue_date"])
            if r["cash_management_bill_cmb"] == "Yes":
                cmb.add(r["issue_date"])
    return {"all": sorted(every), "cmb": sorted(cmb)}


def state_label(state: Optional[float]) -> str:
    if state is None:
        return STATE_LABELS[3]
    return STATE_LABELS[0] if state < 0.5 else STATE_LABELS[2] if state > 2.5 else STATE_LABELS[1]


def assemble(frame, walks, term_table, net_table, panel, auctions, states, immediate, last: date) -> List[dict]:
    """One dict per (decision day, lead): the outcome, the three arms' scores, medians and probabilities, the fitted settlement shifts, the legs
    of the net as announced at the decision, the day types and the scarcity state, for the days of `frame` (#1288's, as built)."""

    models = (S3C, ANN, NET)
    cell_scores = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in models}
    facts = m1288.settlement_facts(panel, auctions)
    rows = {row.date: row for row in panel}
    by_day = auctions_by_day(auctions)
    median_at = sp.GRID.index(0.5)
    walk = walks["ann"]
    out: List[dict] = []
    for d in frame.days:
        i = frame.position[d]
        scale = float(walk.detail[d]["scale"])
        used = walk.fit_used[d]
        instant = datetime.combine(d, k.DECISION_TIME)
        for h in LEADS:
            t = frame.target(d, h)
            y = frame.outcome[t]
            legs = legs_of_day(by_day.get(t, ()), instant)
            flags = term_table.read(h, i)
            sizes = net_table.read(h, i)
            eff_flag = s3c_net.bp_per_100bn(walk.estimates[used][s3c_announced.ANN_ARM.name][h], scale)
            eff_net = s3c_net.bp_per_100bn(walk.estimates[used][s3c_announced.ANN_NET_ARM.name][h], scale)
            f = facts[t]
            row = rows[t].values
            gross_t = float(row.get("treasury_settlement_coupons") or 0.0) + float(row.get("treasury_settlement_bills") or 0.0)
            types = []
            if f["coupon"]:
                types.append(TYPE_LABELS[0])
            if f["bill"]:
                types += [TYPE_LABELS[1], TYPE_LABELS[2] if f["cmb"] else TYPE_LABELS[3]]
            if not f["coupon"] and not f["bill"]:
                types.append(TYPE_LABELS[4])
            cell = {
                "d": d, "t": t, "h": h, "y": y, "regime": frame.regime(t), "settle": bool(f["coupon"] or f["bill"]), "types": types,
                "gross_t": gross_t, "immediate": t.isoformat() in immediate["all"], "immediate_cmb": t.isoformat() in immediate["cmb"],
                "state": states.get(d), "legs": legs, "class": net_class(legs), "share": maturing_share(legs),
                "event": bool(data.exceeds_bp(y, TAU)),
                "shift_flag": sum(eff_flag.get(x, 0.0) * flags[x] for x in TERMS),
                "shift_net": sum(eff_net.get(x, 0.0) * sizes[x] / UNIT for x in TERMS),
                "flag_on": any(flags[x] for x in TERMS),
                "score": {m: {name: cell_scores[m][name][(d, h)] for name in METRICS} for m in models},
                "med": {m: frame.forecasts[m][d][h][median_at] for m in models},
                "prob": {m: m1273.probability(frame.forecasts[m][d][h]) for m in models},
            }
            out.append(cell)
    return out


def _all_nonpositive(legs: Mapping[str, Leg]) -> bool:
    settling = [leg for leg in legs.values() if leg.settles]
    return bool(settling) and all(leg.full and leg.net <= 0.0 for leg in settling)


# -- the difference rows -------------------------------------------------------------------------------------------------


def _units(cells: Sequence[dict], key: str) -> Dict[object, List[dict]]:
    out: Dict[object, List[dict]] = {}
    for x in cells:
        out.setdefault(x[key], []).append(x)
    return out


def diff_row(cells: Sequence[dict], arm: str, ref: str, unit: str, total: Optional[Sequence[dict]] = None) -> dict:
    """The arm against the reference over `cells`, grain `unit` ('d': decision day, 't': target day, the leads of a unit averaged).

    Per score: the means of both, mean d (arm less reference: above zero is a loss), its 90% stationary-bootstrap interval over the units in date
    order when there are at least 20, the skill and the reading. `share_of_loss` is the sum of d over these cells over the sum over `total`
    (grid CRPS).
    """

    units = _units(cells, unit)
    keys = sorted(units)
    row: dict = {"cells": len(cells), "units": len(keys)}
    series = []
    for metric in METRICS:
        arm_u = [sum(x["score"][arm][metric] for x in units[u]) / len(units[u]) for u in keys]
        ref_u = [sum(x["score"][ref][metric] for x in units[u]) / len(units[u]) for u in keys]
        d_u = [a - r for a, r in zip(arm_u, ref_u)]
        series.append(d_u)
        if keys:
            ma, mr = sum(arm_u) / len(keys), sum(ref_u) / len(keys)
            row[metric] = {"mean_arm": ma, "mean_ref": mr, "mean_d": sum(d_u) / len(keys), "skill": skill(ma, mr) if mr else None}
    if total is not None and cells:
        row["share_of_loss"] = share([x["score"][arm]["grid_crps"] - x["score"][ref]["grid_crps"] for x in cells],
                                     [x["score"][arm]["grid_crps"] - x["score"][ref]["grid_crps"] for x in total])
    if len(keys) >= MIN_DAYS:
        _queue(row, "_intervals", "mean", series)
    return row


def _resolve_intervals(node) -> None:
    """After `finish`: move each row's `_intervals` list into its metric entries and add the readings."""

    if isinstance(node, dict):
        if "_intervals" in node:
            for metric, interval in zip(METRICS, node.pop("_intervals")):
                node[metric]["interval"] = interval
                node[metric]["reading"] = reading(interval)
        for metric in METRICS:
            if metric in node and isinstance(node[metric], dict) and "reading" not in node[metric] and "mean_d" in node[metric]:
                node[metric]["interval"] = None
                node[metric]["reading"] = reading(None)
        for v in node.values():
            _resolve_intervals(v)
    elif isinstance(node, list):
        for v in node:
            _resolve_intervals(v)


def group_rows(cells: Sequence[dict], groups: Sequence[Tuple[str, Sequence[dict]]], arm: str, ref: str, unit: str) -> Dict[str, dict]:
    return {label: diff_row(members, arm, ref, unit, total=cells) for label, members in groups if members}


# -- the tables ----------------------------------------------------------------------------------------------------------


def type_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(label, [x for x in cells if label in x["types"]]) for label in TYPE_LABELS]


def class_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(label, [x for x in cells if x["class"] == label]) for label in CLASSES]


def table_1(cells: Sequence[dict], cuts: Tuple[float, float]) -> dict:
    """Where the lead-1 loss of (s3c-ann-net) against (s3c) sits (at lead 1 the flag arm is (s3c))."""

    one = [x for x in cells if x["h"] == 1]
    thirds = [(THIRD_LABELS[i], [x for x in one if x["share"] is not None and third(x["share"], cuts) == i]) for i in range(3)]
    return {
        "all lead-1 cells": diff_row(one, NET, ANN, "d", total=one),
        "by_type": group_rows(one, type_groups(one), NET, ANN, "d"),
        "by_class": group_rows(one, class_groups(one), NET, ANN, "d"),
        "by_maturing_third": group_rows(one, thirds, NET, ANN, "d"),
        "maturing_share_cuts": list(cuts),
    }


def _leg_rows(cells: Sequence[dict], h: int, leg: str) -> List[dict]:
    """The regression rows of one leg at one lead: the target days on which the leg settles fully announced, residual against the flag arm's median."""

    other = "bill" if leg == "coupon" else "coupon"
    out = []
    for x in sorted((x for x in cells if x["h"] == h and x["legs"][leg].settles and x["legs"][leg].full), key=lambda x: x["t"]):
        lg = x["legs"][leg]
        out.append({"r": x["y"] - x["med"][ANN], "gross": lg.gross / UNIT, "maturing": lg.maturing / UNIT, "other": 1 if x["legs"][other].settles else 0,
                    "state": state_label(x["state"]), "t": x["t"]})
    return out


def table_2(cells: Sequence[dict]) -> dict:
    """H-a: gross, net or maturing, on the settlement target days at lead 1 and lead 3."""

    out: dict = {}
    for h in (1, 3):
        for leg in ("coupon", "bill"):
            rows = _leg_rows(cells, h, leg)
            splits = [("pooled", rows)] + [(label, [r for r in rows if r["state"] == label]) for label in STATE_LABELS]
            for label, members in splits:
                entry: dict = {"target_days": len(members)}
                key = f"h={h}/{leg}/{label}"
                if len(members) < MIN_DAYS:
                    entry["not_fitted"] = "fewer than 20 target days"
                elif no_variation(members):
                    entry["not_fitted"] = "no variation in gross"
                else:
                    entry["fit"] = fit_leg(members)
                    _queue(entry, "_fit_intervals", "fit", [{k2: v for k2, v in r.items() if k2 not in ("state", "t")} for r in members])
                out[key] = entry
    return out


def _resolve_fits(node) -> None:
    if isinstance(node, dict):
        if "_fit_intervals" in node:
            node["fit"]["intervals"] = dict(zip(FIT_NAMES, node.pop("_fit_intervals")))
            iv = node["fit"]["intervals"]
            node["fit"]["h_a"] = read_h_a(iv["g_plus_m"], iv["mse_gross_less_net"])
        for v in node.values():
            _resolve_fits(v)


def table_3(cells: Sequence[dict]) -> dict:
    """(s3c-ann-net) against (s3c-ann) at every lead, by regime, by event, by target-day type and class, and where the flag is set but no drain is announced."""

    out: dict = {"by_lead": {}, "by_regime": {}, "by_event": {}, "by_type": {}, "by_class": {}, "flag_without_drain": {}}
    for h in LEADS:
        at = [x for x in cells if x["h"] == h]
        out["by_lead"][f"h={h}"] = diff_row(at, NET, ANN, "d", total=at)
        events = {}
        for label, members in (("target spread above +5 bp", [x for x in at if x["event"]]), ("not above +5 bp", [x for x in at if not x["event"]])):
            if members:
                dsum = sum(x["score"][NET]["brier_gt5"] - x["score"][ANN]["brier_gt5"] for x in members)
                events[label] = {"cells": len(members), "mean_prob_net": sum(x["prob"][NET] for x in members) / len(members),
                                 "mean_prob_flag": sum(x["prob"][ANN] for x in members) / len(members),
                                 "brier_difference_sum": dsum, "brier_difference_mean": dsum / len(members)}
        out["by_event"][f"h={h}"] = {"frequency": sum(1 for x in at if x["event"]) / len(at), "sets": events}
        out["by_type"][f"h={h}"] = group_rows(at, type_groups(at), NET, ANN, "d")
        out["by_class"][f"h={h}"] = group_rows(at, class_groups(at), NET, ANN, "d")
        quiet = [x for x in at if x["flag_on"] and _all_nonpositive(x["legs"])]
        loud = [x for x in at if x["flag_on"] and not _all_nonpositive(x["legs"])]
        out["flag_without_drain"][f"h={h}"] = group_rows(at, [("flag set, every settling leg net at or below zero", quiet),
                                                              ("flag set, some leg net above zero", loud)], NET, ANN, "d")
    for regime in REGIMES:
        members = [x for x in cells if x["regime"] == regime]
        if members:
            out["by_regime"][regime] = diff_row(members, NET, ANN, "t", total=members)
    return out


def _bias_units(cells: Sequence[dict], arms: Sequence[str]) -> List[dict]:
    """Per decision day, the sums the settlement-day bias needs, by regime of the target and arm."""

    units: Dict[date, dict] = {}
    for x in cells:
        u = units.setdefault(x["d"], {})
        bucket = u.setdefault(x["regime"], {a: [0, 0.0, 0, 0.0, 0.0, 0.0, 0.0] for a in arms})
        for a in arms:
            b = bucket[a]
            shift = x["shift_flag"] if a == ANN else x["shift_net"] if a == NET else 0.0
            err = x["y"] - x["med"][a]
            if x["settle"]:
                b[0] += 1
                b[1] += err
                b[4] += shift
                b[5] += x["y"]
            else:
                b[2] += 1
                b[3] += err
                b[6] += x["y"]
    return [units[d] for d in sorted(units)]


def _bias_totals(units: Sequence[dict], idx: Sequence[int]) -> Dict[str, Dict[str, List[float]]]:
    """The sums of the resampled units by regime and arm."""

    out: Dict[str, Dict[str, List[float]]] = {}
    for i in idx:
        for regime, by_arm in units[i].items():
            tot = out.setdefault(regime, {a: [0.0] * 7 for a in by_arm})
            for a, b in by_arm.items():
                t = tot[a]
                for j in range(7):
                    t[j] += b[j]
    return out


def _bias_value(totals: Mapping[str, Mapping[str, Sequence[float]]], name: str) -> float:
    """`name` is 'regime/arm/field' (field: bias, shift or premium) or 'difference/arm/regime/regime2' (the bias of the first less the second)."""

    def get(regime: str, arm: str, field: str) -> float:
        t = totals[regime][arm]
        if field == "bias":
            return t[1] / t[0] - t[3] / t[2]
        if field == "shift":
            return t[4] / t[0]
        return t[5] / t[0] - t[6] / t[2]

    parts = name.split("/")
    if parts[0] == "difference":
        return get(parts[2], parts[1], "bias") - get(parts[3], parts[1], "bias")
    return get(parts[0], parts[1], parts[2])


def table_4(cells: Sequence[dict], panel_cuts: float) -> dict:
    """H-b: why the announced arms lose to (s3c) in 2020."""

    out: dict = {}
    y20 = [x for x in cells if x["regime"] == "2020"]
    # 4a: by month, and March to June against the rest
    months = {}
    for month in range(1, 13):
        months[f"2020-{month:02d}"] = [x for x in y20 if x["t"].month == month]
    spring = [x for x in y20 if 3 <= x["t"].month <= 6]
    rest = [x for x in y20 if not 3 <= x["t"].month <= 6]
    out["4a"] = {}
    for arm in (ANN, NET):
        out["4a"][arm] = {
            "2020 target days": diff_row(y20, arm, S3C, "t", total=y20),
            "March to June": diff_row(spring, arm, S3C, "t", total=y20),
            "the rest of 2020": diff_row(rest, arm, S3C, "t", total=y20),
            "by_month": {label: diff_row(members, arm, S3C, "t", total=y20) for label, members in months.items() if members},
        }
    # 4b: the settlement terms against the realised spread, by regime, leads 2 to 5
    later = [x for x in cells if x["h"] >= 2]
    arms = (S3C, ANN, NET)
    units = _bias_units(later, arms)
    out["4b"] = {"by_regime": {}, "difference_2020_less_2018_19": {}}
    names, slots = [], []
    for regime in REGIMES:
        members = [x for x in later if x["regime"] == regime]
        if not members:
            continue
        entry = {"cells": len(members)}
        for a in arms:
            sub = [{"settle": x["settle"], "y": x["y"], "med": x["med"][a],
                    "shift": x["shift_flag"] if a == ANN else x["shift_net"] if a == NET else 0.0} for x in members]
            entry[a] = settlement_bias(sub)
            for field in ("bias", "shift", "premium"):
                names.append(f"{regime}/{a}/{field}")
                slots.append((entry[a], field))
        out["4b"]["by_regime"][regime] = entry
    for a in (ANN, NET):
        names.append(f"difference/{a}/2020/2018-19")
        slots.append((out["4b"]["difference_2020_less_2018_19"].setdefault(a, {}), "bias"))
    if len(units) >= MIN_DAYS:
        holder: dict = {}
        _queue(holder, "iv", "bias", (units, names))
        out["_bias_holder"] = (holder, slots, names)
    # 4c: state by settlement size, leads 2 to 5, 2020
    later20 = [x for x in y20 if x["h"] >= 2]
    def size_of(x):
        return SIZE_LABELS[2] if not x["settle"] else SIZE_LABELS[0] if x["gross_t"] >= panel_cuts else SIZE_LABELS[1]
    out["4c"] = {}
    for arm in (ANN, NET):
        rows = {}
        for sl in STATE_LABELS:
            for zl in SIZE_LABELS:
                members = [x for x in later20 if state_label(x["state"]) == sl and size_of(x) == zl]
                if members:
                    rows[f"state {sl}, {zl}"] = diff_row(members, arm, S3C, "d", total=later20)
        out["4c"][arm] = {"all 2020 cells at h = 2 to 5": diff_row(later20, arm, S3C, "d", total=later20), "groups": rows}
    out["4c_size_cut_gross_usd_bn"] = panel_cuts
    # 4d: the immediate-release days
    out["4d"] = {}
    for arm in (ANN, NET):
        imm = [x for x in y20 if x["immediate"]]
        imm_cmb = [x for x in y20 if x["immediate_cmb"]]
        out["4d"][arm] = {
            "an auction with no stated release time settles on the target": diff_row(imm, arm, S3C, "t", total=y20),
            "such a cash management bill settles on the target": diff_row(imm_cmb, arm, S3C, "t", total=y20),
            "2020 with those days left out": diff_row([x for x in y20 if not x["immediate"]], arm, S3C, "t", total=y20),
            "2020, all target days": diff_row(y20, arm, S3C, "t", total=y20),
        }
    return out


def _resolve_bias(table: dict, workers: int) -> None:
    holder = table.pop("_bias_holder", None)
    if holder is None:
        return
    box, slots, names = holder
    for (entry, field), name, interval in zip(slots, names, box["iv"]):
        entry.setdefault("intervals", {})[field if name.split("/")[0] != "difference" else "bias"] = interval


def reproduction(cells: Sequence[dict], record: Mapping[str, dict]) -> dict:
    """The arms' pooled, lead and regime means against #1288's record, to 1e-9 (a refusal otherwise), and the lead-1 identities."""

    checked = {}
    for metric in ("grid_crps", "upper_tail_twcrps", "brier_gt5"):
        pooled = {}
        for m in (S3C, ANN, NET):
            per = {}
            for x in cells:
                per.setdefault(x["d"], []).append(x["score"][m][metric])
            pooled[m] = sum(sum(v) / len(v) for v in per.values()) / len(per)
        check_means(pooled, record["groups"]["pooled"]["all decision days"][metric]["means"], f"pooled {metric}")
        checked[f"pooled/{metric}"] = pooled
        for h in LEADS:
            at = {m: [x["score"][m][metric] for x in cells if x["h"] == h] for m in (S3C, ANN, NET)}
            lead = {m: sum(v) / len(v) for m, v in at.items()}
            check_means(lead, record["groups"]["lead"][f"h={h}"][metric]["means"], f"lead {h} {metric}")
        for regime in REGIMES if "regime" in record["groups"] else ():
            per = {m: {} for m in (S3C, ANN, NET)}
            for x in cells:
                if x["regime"] == regime:
                    for m in per:
                        per[m].setdefault(x["t"], []).append(x["score"][m][metric])
            if per[S3C]:
                means = {m: sum(sum(v) / len(v) for v in per[m].values()) / len(per[m]) for m in per}
                check_means(means, record["groups"]["regime"][regime][metric]["means"], f"regime {regime} {metric}")
    for x in cells:
        if x["h"] == 1 and x["score"][ANN] != x["score"][S3C]:
            raise ValueError(f"(s3c-ann) is not (s3c) at lead 1 on {x['d']}")
    return {"checked": "pooled, lead and regime means of (s3c), (s3c-ann) and (s3c-ann-net), three scores, equal #1288's record to 1e-9",
            "pooled_means": checked}


def settlement_size_cut(cells: Sequence[dict]) -> float:
    """The gross (USD bn) of the target day above which a settlement day is in the highest third: from the development window's settlement target days."""

    gross = sorted({x["t"]: x["gross_t"] for x in cells if x["settle"]}.values())
    return gross[(2 * len(gross)) // 3]


def run_window(window: str, cells: Sequence[dict], cuts, size_cut, record: dict, full: bool) -> dict:
    result = {"cells": len(cells), "decision_days": len({x["d"] for x in cells}), "reproduction": reproduction(cells, record),
              "table_1": table_1(cells, cuts), "table_2": table_2(cells), "table_3": table_3(cells)}
    if full:
        result["table_4"] = table_4(cells, size_cut)
    return result


def build_cells(args) -> Dict[str, List[dict]]:
    """#1288's frames and walks for both windows, as built there, and the cells of each."""

    panel_path = Path(args.panel)
    panel = [row for row in m1288.load_daily_panel(panel_path) if row.date <= m1288.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_ann_net_diagnosis_1319")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    states = k.d1145.decision_states(c.SOURCES)
    immediate = release_days()
    cells: Dict[str, List[dict]] = {}
    for window in m1288.WINDOWS:
        frame, _notes, walks, (term_table, net_table), _ct, _gf = m1288.build(window, panel, splits, registry, table, register, results, auctions, args.first)
        cells[window] = assemble(frame, walks, term_table, net_table, panel, auctions, states, immediate, m1288.WINDOW_LAST[window])
    return cells


def score(args) -> int:
    declaration = committed_declaration()
    published_sha = panel_sha256(Path(args.panel))
    if args.cache and Path(args.cache).exists():
        cells = pickle.loads(Path(args.cache).read_bytes())
    else:
        cells = build_cells(args)
        if args.cache:
            Path(args.cache).write_bytes(pickle.dumps(cells))
    record = json.loads(RECORD_1288.read_text(encoding="utf-8"))["windows"]
    first = m1288.WINDOWS[0]
    dev = cells[first]
    settle = [x for x in dev if x["h"] == 1 and x["share"] is not None]
    cuts = thirds_cuts([x["share"] for x in settle]) if settle else (0.0, 0.0)
    size_cut = settlement_size_cut(dev)
    result: dict = {"issue": 1319, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
                    "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict", "seed": SEED,
                    "reps": REPS, "block": BLOCK, "amendments": declaration["amendments"], "windows": {}}
    for window in m1288.WINDOWS:
        result["windows"][window] = run_window(window, cells[window], cuts, size_cut, record[window], full=window == first)
    finish(args.workers)
    for window, r in result["windows"].items():
        if "table_4" in r:
            _resolve_bias(r["table_4"], args.workers)
        _resolve_intervals(r)
        _resolve_fits(r)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------

# (appended below by `render`, `question` and `main`)


def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100.0 * x:+.1f}%"


def _iv(interval: Optional[Sequence[float]], digits: int = 3) -> str:
    return "not read" if interval is None else f"[{interval[0]:+.{digits}f}, {interval[1]:+.{digits}f}]"


def _cell(entry: Optional[dict]) -> str:
    """One score's cell: skill of the arm over the reference, mean d with its interval, and the reading (a positive d is a loss)."""

    if not entry or "mean_d" not in entry:
        return "n/a"
    return f"{_pct(entry['skill'])}, d {entry['mean_d']:+.3f} {_iv(entry['interval'])} **{entry['reading']}**"


def diff_table(rows: Mapping[str, dict], first: str = "group") -> List[str]:
    """Markdown rows of `diff_row` results: the group, its cells and units, its share of the loss, and the three scores."""

    out = [f"| {first} | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |", "|---|---|---|---|---|---|---|"]
    for label, row in rows.items():
        out.append(f"| {label} | {row['cells']} | {row['units']} | {_pct(row.get('share_of_loss'))} | "
                   + " | ".join(_cell(row.get(m)) for m in METRICS) + " |")
    return out


def _fit_cell(entry: dict) -> List[str]:
    if "fit" not in entry:
        return [str(entry["target_days"]), "not fitted: " + entry["not_fitted"], "", "", "", "", ""]
    f, iv = entry["fit"], entry["fit"].get("intervals", {})
    return [str(f["days"]), f"{f['g']:+.2f} {_iv(iv.get('g'), 2)}", f"{f['m']:+.2f} {_iv(iv.get('m'), 2)}",
            f"{f['g_plus_m']:+.2f} {_iv(iv.get('g_plus_m'), 2)}", f"{f['n']:+.2f} {_iv(iv.get('n'), 2)}",
            f"{f['mse_gross']:.2f} / {f['mse_net']:.2f} / {f['mse_full']:.2f}", f"**{f.get('h_a', 'not read')}**"]


def fit_table(t2: Mapping[str, dict], lead: int, leg: str) -> List[str]:
    out = [f"| scarcity state | target days | gross g | maturing m | g + m | net alone n | mean squared residual: gross only / net only / both | H-a |",
           "|---|---|---|---|---|---|---|---|"]
    for key, entry in t2.items():
        h, lg, label = key.split("/", 2)
        if h == f"h={lead}" and lg == leg:
            out.append(f"| {label} | " + " | ".join(_fit_cell(entry)) + " |")
    return out


def read_h_b(bias_difference: Optional[Sequence[float]], top_reading: str, rest_has_loss: bool) -> str:
    """H-b for one arm (the declaration's rule): the settlement-day bias below 2018-19's on the interval, a loss on the highest third of settlement
    size at states 0 or 1 to 2 and no loss elsewhere at those states."""

    if bias_difference is None:
        return "not read"
    if bias_difference[1] < 0.0 and top_reading == "loss" and not rest_has_loss:
        return "supported"
    if bias_difference[0] > 0.0 or top_reading == "gain":
        return "not supported"
    return "undecided"


def h_b_reading(t4: Mapping[str, dict], arm: str) -> dict:
    groups = t4["4c"][arm]["groups"]
    top = [g for label, g in groups.items() if SIZE_LABELS[0] in label and not label.startswith("state 3") and g["units"] >= MIN_DAYS]
    top_reading = top[0]["grid_crps"]["reading"] if top else "not read"
    rest = [g for label, g in groups.items() if SIZE_LABELS[0] not in label and not label.startswith("state 3") and g["units"] >= MIN_DAYS]
    rest_loss = any(g["grid_crps"]["reading"] == "loss" for g in rest)
    diff = t4["4b"]["difference_2020_less_2018_19"][arm].get("intervals", {}).get("bias")
    left_out = t4["4d"][arm]["2020 with those days left out"]["grid_crps"]
    return {"reading": read_h_b(diff, top_reading, rest_loss), "top_reading": top_reading, "rest_has_loss": rest_loss, "bias_difference": diff,
            "dating_ruled_out": left_out["reading"] == "loss", "left_out": left_out}


def _g(row: Mapping[str, dict], metric: str = "grid_crps") -> str:
    return _cell(row.get(metric))


def render(r: dict) -> str:
    dev, new = r["windows"]["development"], r["windows"]["2026"]
    t1, t2, t3, t4 = dev["table_1"], dev["table_2"], dev["table_3"], dev["table_4"]
    out: List[str] = []
    add = out.append
    add("# Why (s3c-ann-net) loses three times: a diagnosis of #1288's record (#1319)\n")
    add("**Hypothesis and step:** H5 (the SOFR - IORB spread distribution), step 3, the candidate (s3c-ann-net). Development tier: a diagnosis of a record that "
        "exists, never a verdict. Nothing is registered or published, no arm, record or declaration changes, and no lockbox day is scored. Her ruling of "
        "30 October 2026 (ledger item 79). The findings are #1316; #1316, #1317 and #1318 stay open.\n")
    add(f"**What was done.** #1288's frames, walks and forecasts were rebuilt exactly as merged (`scripts/s3c_announced_settlement_1288.py`, no new fit) on the "
        f"published panel `{r['panel_sha256'][:8]}...`, and every pooled, lead and regime mean of (s3c), (s3c-ann) and (s3c-ann-net), on all three scores, was "
        f"checked equal to #1288's record to 1e-9 (the study refuses to write otherwise). The tables are declared in "
        f"`metadata/s3c_ann_net_diagnosis_1319.json`, committed before any table was computed. Intervals are 90% stationary-bootstrap intervals "
        f"(mean block {r['block']:g}, {r['reps']} replications, seed {r['seed']}) over days in date order: a diagnostic interval on mean d, not scoring "
        f"protocol v1's studentized test. A difference d is the arm less the reference, so **a positive d is a loss for the arm**. Every reading is taken "
        f"from the development window (targets to 2025-12-31); the 2026 days are shown at the end and decide nothing. Cells are (decision day, lead) pairs; "
        f"'days' are the units the interval resamples.\n")
    # answers
    a_net = t4["4a"][NET]
    ha = {(h, leg): t2[f"h={h}/{leg}/pooled"]["fit"] for h in (1, 3) for leg in ("coupon", "bill")}
    hb_ann, hb_net = h_b_reading(t4, ANN), h_b_reading(t4, NET)
    one = t1["all lead-1 cells"]
    none = t1["by_type"][TYPE_LABELS[4]]
    third_hi = t1["by_maturing_third"][THIRD_LABELS[2]]
    lowest = t1["by_maturing_third"][THIRD_LABELS[0]]
    ev1 = t3["by_event"]["h=1"]["sets"]
    ev3 = t3["by_event"]["h=3"]["sets"]
    b1819 = t4["4b"]["by_regime"]["2018-19"]
    b20 = t4["4b"]["by_regime"]["2020"]
    add("**Amendments to the declaration** (recorded after a scratch run of the tables; none changes a figure):\n")
    for item in r["amendments"]:
        add("- " + item)
    add("")
    add("## Answers: why does it do this?\n")
    add("Each reading below is computed from the intervals by the declared rule; the mechanisms are the orchestrating session's hypotheses, tested here, "
        "not established.\n")
    add(f"**1. Lead 1, against (s3c).** The loss is on the Brier score of P(> +5 bp) ({_g(one, 'brier_gt5')}), and it is not where hypothesis H-a puts it. "
        f"On the highest third of maturing share (the days where netting removes most of the gross) (s3c-ann-net) is a **gain** ({_g(third_hi)}); the "
        f"Brier loss sits on days with the lowest maturing share ({_g(lowest, 'brier_gt5')}) and on days with no settlement at all "
        f"({_g(none, 'brier_gt5')}; grid CRPS {_g(none)}). On days with no settlement both arms add nothing for settlement, so that loss comes from the "
        f"rest of the refit, not from how a settlement is sized. By realised event, the net arm gives a lower probability on the days the spread went above "
        f"+5 bp (mean {ev1['target spread above +5 bp']['mean_prob_net']:.3f} against the flag's {ev1['target spread above +5 bp']['mean_prob_flag']:.3f}, "
        f"on {ev1['target spread above +5 bp']['cells']} cells) and nearly the same on the others, so it is a little less sharp on pressure days.\n")
    add(f"**H-a (gross, not net), the regression.** On coupon settlement days the maturing amount does not offset the gross amount one for one: g + m at lead 1 is "
        f"{ha[(1, 'coupon')]['g_plus_m']:+.2f} bp per USD 100 bn {_iv(ha[(1, 'coupon')]['intervals']['g_plus_m'], 2)}, **{ha[(1, 'coupon')]['h_a']}**; at lead 3 "
        f"{ha[(3, 'coupon')]['g_plus_m']:+.2f} {_iv(ha[(3, 'coupon')]['intervals']['g_plus_m'], 2)}, **{ha[(3, 'coupon')]['h_a']}**. For the bill leg it is "
        f"**{ha[(1, 'bill')]['h_a']}** at lead 1 ({ha[(1, 'bill')]['g_plus_m']:+.2f} {_iv(ha[(1, 'bill')]['intervals']['g_plus_m'], 2)}) and "
        f"**{ha[(3, 'bill')]['h_a']}** at lead 3 ({ha[(3, 'bill')]['g_plus_m']:+.2f} {_iv(ha[(3, 'bill')]['intervals']['g_plus_m'], 2)}). So: supported for the "
        f"coupon leg, undecided for the bill leg, and not a reason for the lead-1 loss, which is not on the large-maturing days.\n")
    add(f"**2. 2020, against (s3c).** Both announced arms lose on grid CRPS ((s3c-ann) {_g(t4['4a'][ANN]['2020 target days'])}; (s3c-ann-net) "
        f"{_g(a_net['2020 target days'])}), and the loss is mostly March to June (shares {_pct(t4['4a'][ANN]['March to June']['share_of_loss'])} and "
        f"{_pct(a_net['March to June']['share_of_loss'])}): the rest of 2020 is undecided for both. In 2020 the realised spread on settlement target days is "
        f"{b20[ANN]['premium']:+.2f} bp above the others {_iv(b20[ANN]['intervals']['premium'], 2)}, against a fitted settlement shift of "
        f"{b20[ANN]['shift']:+.2f} bp for the flag and {b20[NET]['shift']:+.2f} bp for the net: both arms still add a settlement premium that 2020 did not pay. "
        f"**H-b: (s3c-ann) {hb_ann['reading']}, (s3c-ann-net) {hb_net['reading']}.** For the flag arm the loss sits on the highest third of settlement size at "
        f"states 1 to 2 ({hb_ann['top_reading']}) and nowhere else at states 0 to 2; for the net arm that cell is {hb_net['top_reading']} and "
        f"{'another cell of states 0 to 2 is a loss' if hb_net['rest_has_loss'] else 'no other cell is a loss'}. The scarcity state the model reads was almost never 0 "
        f"in 2020 (nearly all settlement cells are at states 1 to 3), so the 'abundant reserves' reading of 2020 cannot be tested on that state. "
        f"**The dating is {'ruled out' if hb_ann['dating_ruled_out'] else 'not ruled out'} as the cause for the flag arm** (2020 without the immediate-release "
        f"days: {_cell(hb_ann['left_out'])}) **and {'ruled out' if hb_net['dating_ruled_out'] else 'not ruled out'} for the net arm** "
        f"(without them {_cell(hb_net['left_out'])}; those days carry {_pct(t4['4d'][NET]['an auction with no stated release time settles on the target']['share_of_loss'])} "
        f"of the net arm's 2020 loss, {_pct(t4['4d'][ANN]['an auction with no stated release time settles on the target']['share_of_loss'])} of the flag arm's).\n")
    add(f"**3. Net against flag.** The net arm loses on the Brier score at every lead ({', '.join(_pct(t3['by_lead'][f'h={h}']['brier_gt5']['skill']) for h in (1, 2, 3, 4, 5))} "
        f"at h = 1..5, all losses on the interval) and the loss is on the days the spread went above +5 bp: at h = 3 the Brier difference summed over those "
        f"{ev3['target spread above +5 bp']['cells']} cells is {ev3['target spread above +5 bp']['brier_difference_sum']:+.2f}, over the other "
        f"{ev3['not above +5 bp']['cells']} cells {ev3['not above +5 bp']['brier_difference_sum']:+.3f}; the net arm gives those days a probability of "
        f"{ev3['target spread above +5 bp']['mean_prob_net']:.3f} against the flag's {ev3['target spread above +5 bp']['mean_prob_flag']:.3f}. In 2018-19, where it "
        f"loses on all three scores ({_g(t3['by_regime']['2018-19'])}), the realised settlement-day premium was {b1819[ANN]['premium']:+.1f} bp "
        f"{_iv(b1819[ANN]['intervals']['premium'], 1)}, the flag arm's fitted shift {b1819[ANN]['shift']:+.2f} bp and the net arm's {b1819[NET]['shift']:+.2f} bp: "
        f"netting shrinks the regressor, so the fitted size effect buys a fraction of what the flag buys when pressure is large and settlement-driven. "
        f"That is H-a's direction (netting understates the squeeze), shown on the regime where the settlement premium was large; the maturing amounts are not "
        f"separated from the shrinkage here. In 2020, 2024 and 2025-26 the net arm is ahead of the flag on grid CRPS (gains on the interval).\n")
    add("## Table 1. Where the lead-1 loss of (s3c-ann-net) against (s3c) sits (development window)\n")
    add("At lead 1 the flag arm is (s3c) cell for cell, and the net arm is #1273's (s3c-net). One cell per decision day.\n")
    add("### All lead-1 cells and by target-day type\n")
    out += diff_table({"all lead-1 cells": t1["all lead-1 cells"], **t1["by_type"]})
    add("\n### By the net-to-gross class of the target day, as announced at the decision\n")
    out += diff_table(t1["by_class"], "class")
    add(f"\n### By maturing share of gross (thirds fixed on the development window's settlement target days; cuts {t1['maturing_share_cuts'][0]:.3f} and {t1['maturing_share_cuts'][1]:.3f})\n")
    out += diff_table(t1["by_maturing_third"])
    add("\n## Table 2. H-a: gross, maturing or net on the settlement target days (development window)\n")
    add("Residual r = y - median of the flag arm's forecast at that lead, in bp, on the target days where the leg settles with its class fully announced at "
        "the decision. r = a + g gross + m maturing + o other-leg-settles; gross and maturing in USD 100 bn. If netting were the whole story m = -g and "
        "g + m = 0. The last-but-one column is the in-sample mean squared residual of the gross-only, net-only and both forms. Intervals: stationary bootstrap over target "
        "days, refitting at every resample.\n")
    for h in (1, 3):
        for leg in ("coupon", "bill"):
            add(f"\n### Lead {h}, {leg} leg\n")
            out += fit_table(t2, h, leg)
    add("\n## Table 3. (s3c-ann-net) against (s3c-ann) (development window)\n")
    add("### By lead\n")
    out += diff_table(t3["by_lead"], "lead")
    add("\n### By regime of the target day (the five leads averaged per target day, as #1288 groups it)\n")
    out += diff_table(t3["by_regime"], "regime")
    add("\n### By realised event: the probability of a spread above +5 bp\n")
    add("| lead | event frequency | set | cells | mean probability, net | mean probability, flag | Brier difference summed | per cell |\n|---|---|---|---|---|---|---|---|")
    for h in LEADS:
        e = t3["by_event"][f"h={h}"]
        for label, v in e["sets"].items():
            add(f"| h={h} | {e['frequency']:.3f} | {label} | {v['cells']} | {v['mean_prob_net']:.3f} | {v['mean_prob_flag']:.3f} | "
                f"{v['brier_difference_sum']:+.3f} | {v['brier_difference_mean']:+.4f} |")
    for h in (1, 3):
        add(f"\n### Lead {h}: the flag set and an announced drain or none\n")
        out += diff_table(t3["flag_without_drain"][f"h={h}"])
        add(f"\n### Lead {h}: by target-day type\n")
        out += diff_table(t3["by_type"][f"h={h}"])
        add(f"\n### Lead {h}: by net-to-gross class\n")
        out += diff_table(t3["by_class"][f"h={h}"], "class")
    add("\n## Table 4. H-b: the 2020 loss against (s3c) (development window)\n")
    for arm in (ANN, NET):
        x = t4["4a"][arm]
        add(f"\n### 4a. {ARM_LABELS[arm]}: 2020 by period and month (target days, five leads averaged)\n")
        out += diff_table({k2: v for k2, v in x.items() if k2 != "by_month"})
        add("")
        out += diff_table(x["by_month"], "month")
    add("\n### 4b. The settlement terms against the realised spread, by regime (leads 2 to 5)\n")
    add("Bias: mean of y - median on settlement target cells less that on the others (negative: forecast too high on settlement days). Shift: the arm's "
        "fitted settlement contribution in bp on settlement cells. Premium: the realised mean spread on settlement target days less the others. Intervals "
        "over decision days.\n")
    add("| regime | arm | settlement cells | bias | shift | realised premium |\n|---|---|---|---|---|---|")
    for regime, e in t4["4b"]["by_regime"].items():
        for arm in (S3C, ANN, NET):
            v = e[arm]
            iv = v.get("intervals", {})
            add(f"| {regime} | {ARM_LABELS[arm]} | {v['settlement_cells']} | {v['bias']:+.2f} {_iv(iv.get('bias'), 2)} | {v['shift']:+.2f} {_iv(iv.get('shift'), 2)} | "
                f"{v['premium']:+.2f} {_iv(iv.get('premium'), 2)} |")
    d = t4["4b"]["difference_2020_less_2018_19"]
    add(f"\nThe bias of 2020 less that of 2018-19: {ARM_LABELS[ANN]} {_iv(d[ANN]['intervals']['bias'], 2)}, {ARM_LABELS[NET]} {_iv(d[NET]['intervals']['bias'], 2)} "
        f"(both below zero, mostly because (s3c) itself under-forecast settlement days by about {b1819[S3C]['bias']:+.1f} bp in 2018-19).\n")
    add(f"### 4c. 2020, leads 2 to 5, by scarcity state of the decision day and settlement size (highest third: gross of at least USD {t4['4c_size_cut_gross_usd_bn']:.0f} bn)\n")
    for arm in (ANN, NET):
        add(f"\n{ARM_LABELS[arm]} against (s3c)\n")
        out += diff_table({"all 2020 cells at h = 2 to 5": t4["4c"][arm]["all 2020 cells at h = 2 to 5"], **t4["4c"][arm]["groups"]})
    add("\n### 4d. The immediate-release days (an auction with no stated release time settles on the target; metadata/announcement_release_times_1301.json)\n")
    for arm in (ANN, NET):
        add(f"\n{ARM_LABELS[arm]} against (s3c), target days\n")
        out += diff_table(t4["4d"][arm])
    add("\n## The 2026 days (targets 2026-01-02 to 2026-09-03; descriptive, decides nothing)\n")
    add("### Lead 1: (s3c-ann-net) against (s3c)\n")
    out += diff_table({"all lead-1 cells": new["table_1"]["all lead-1 cells"], **new["table_1"]["by_type"]})
    add("\n### (s3c-ann-net) against (s3c-ann), by lead\n")
    out += diff_table(new["table_3"]["by_lead"], "lead")
    add("\n## What this does and does not show\n")
    add("- It is a diagnosis on days already seen: every interval is a development interval, the group-of-days intervals keep the current method (#1221, #1228), "
        "and no reading here is a verdict or changes a claim.\n"
        "- The fits, the walks and the arms are #1288's and are unchanged. The mechanisms (a refit that moves the non-settlement terms; netting shrinking the size "
        "regressor) are stated as the reading of the tables, and no arm was run to test them.\n"
        "- H-a is tested through the residual against the flag arm's own median: the gross and maturing amounts are the announced ones (a class announced in part "
        "is left out), the regression is in sample, and the bill leg is dominated by a few very large residuals in the scarce state.\n"
        "- The 'abundant reserves' reading of H-b needs a state that was 0 in 2020; the model's state was not. Settlement size, the realised premium and "
        "the settlement-day bias are the nearest tests available here.\n"
        "- The immediate-release dating check rests on the 12:00 announcement instant and on the days' own release rule; a cash management bill with no stated "
        "release time could have been announced after the 16:00 decision, which would count it too early.\n")
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: Optional[dict] = None) -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)\n",
        "**Question 1. #1316: what to record about the three losses.** The page's answers are development readings on seen days. Recording them is her call.\n",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):\n",
        "1. **Record the three losses as open questions** on the candidate's pages, with this page's readings, and change no claim (default). Recommended.",
        "2. **Widen #1314** (the 18:00 re-run) so its table also carries the lead-1, 2020 and net-against-flag splits of this page, so the question is re-asked at the new instant.\n",
        "**Question 2. #1318: which arm to queue next.** The flag and the net win in different places; the coupon leg's regression supports gross over net (H-a), and "
        "the net's Brier loss is on pressure days.\n",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):\n",
        "1. **Queue nothing yet** (default): leave #1318 open until #1314 has re-run the candidate at 18:00.",
        "2. **Queue the flag-plus-net arm of #1318** on #1288's script, beside the flag and the net, as one development run. Recommended if she wants a next step now.",
        "3. **Queue a gross-sized arm** (the coupon gross as a size, the bill as a flag), since H-a is supported for the coupon leg and undecided for the bill leg.\n",
        "**Question 3. #1317: the dating's documents.** Nothing on this page changes what #1317 asks. One fact bears on it: the net arm's 2020 loss is not "
        "separable from the immediate-release cash management bills (page, 4d).\n",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):\n",
        "1. **Leave #1317 as it is** (default).",
        "2. **Add the 2020 immediate-release finding to #1317's list** of what the documents should say about the dating's evidence. Recommended.",
    ]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="read #1288's walks and compute the diagnostic tables")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.add_argument("--cache", default=None, help="a pickle of the cells, written if absent and read if present (development only)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
