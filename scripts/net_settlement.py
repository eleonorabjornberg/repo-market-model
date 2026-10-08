"""Net Treasury cash settlement as an input to the pressure classifiers (#426, track N of #374).

A scratch measurement, not a record: it writes CSV and JSON to the paths it is given and nothing
into `docs/runs/`. The setting (the announcement instant), the columns and the two classifiers
extended are in `metadata/net_settlement.json`, and the candidates in `metadata/pressure_judge.json`;
`run` refuses a declaration that is not committed and unchanged. The columns are off in every
published declaration and switched on for these runs only.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/net_settlement.py reconcile --panel AUG3.csv --published PUBLISHED.csv --output OUT/reconcile.json
    PYTHONPATH=src python3 scripts/net_settlement.py run --panel AUG3.csv --horizon H --output OUT/net_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel AUG3.csv --horizon H --output OUT/b_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel AUG3.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/b_h1.json OUT/net_h1.json ...
    PYTHONPATH=src python3 scripts/net_settlement.py pair --panel AUG3.csv --output OUT/pair.json OUT/net_h?.json

* `panel` adds the three columns (`repo_model.net_settlement`) to the scratch panel and keeps the rows
  up to 2025-12-31 (`docs/decisions/lockbox.md`).
* `reconcile` sets the snapshot's gross offerings against the published panel's gross settlement
  columns, cross-checks the announced maturing amounts against the table's own earlier auctions,
  reports the SOMA add-on, the groups with no maturing figure, and how much of the next five days'
  settlement was announced at each decision.
* `run` scores the two classifiers with and without the columns on the shared fold grid
  (minimum history 61, refit every 21 days, scored days through 2025-12-31), recalibrated out of fold,
  and writes the judge's `forecasts` shape.
* `pair` reports the paired Brier difference of each candidate against its control with a
  stationary-bootstrap interval, overall and by regime and pressure-day type.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import functools
import hashlib
import importlib.util
import json
import statistics
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, hierarchical_logistic as hl, measurement_fields, ml, net_settlement as ns  # noqa: E402
from repo_model import pressure, pressure_judge as pj, scarcity  # noqa: E402
from repo_model import scarcity_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel, next_business_day  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402

DECLARATION = REPO / "metadata" / "net_settlement.json"
ONSET_DECLARATION = REPO / "metadata" / "onset_classifier.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
END = date(2025, 12, 31)
HIERARCHICAL, HIERARCHICAL_NET = "hierarchical_logistic", "hierarchical_logistic_net"
ONSET, ONSET_NET = "onset_logistic+recalibrated", "onset_logistic_net+recalibrated"
SETTLEMENT = "treasury_settlement"
MINIMUM_HISTORY, REFIT_EVERY, DECISION = 61, 21, time(16, 0)


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed(path: Path) -> str:
    """The file's content, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()


@contextlib.contextmanager
def switched_on():
    """The scarcity state, #377's fields and the net settlement columns in the feature map, for this run only."""

    fields = {**measurement_fields.COLUMN_FIELDS, **ns.COLUMN_FIELDS}
    with scarcity.measurement_declaration(), mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()},
            }
        ),
    ):
        yield


def _keyed(value):
    """`value` with every dict key a string, so it can be written sorted."""

    if isinstance(value, dict):
        return {str(key): _keyed(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_keyed(item) for item in value]
    return value


def _cell(value):
    return "" if value is None else repr(float(value))


def _auctions():
    declaration = ns.load_declaration(DECLARATION)
    directory = REPO / declaration["snapshot"]
    manifest = json.loads(next(directory.glob("*.manifest.json")).read_text())
    payload = directory / Path(manifest["path"]).name
    if hashlib.sha256(payload.read_bytes()).hexdigest() != manifest["sha256"]:
        raise SystemExit(f"{payload} does not match its manifest checksum")
    return declaration, ns.load_snapshot(payload, declaration), payload, manifest


def panel_command(args) -> int:
    declaration, auctions, payload, manifest = _auctions()
    rows = [row for row in load_daily_panel(args.panel) if row.date <= END]
    built = ns.with_net_settlement(rows, auctions, declaration)
    ns.check_known_columns(built, auctions, declaration)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + list(ns.COLUMNS)))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    summary = {
        "output": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "rows": len(built),
        "first": built[0].date.isoformat(),
        "last": built[-1].date.isoformat(),
        "snapshot_sha256": manifest["sha256"],
        "snapshot": str(payload.relative_to(REPO)),
        "columns": {
            name: {
                "min": min(r.values[name] for r in built),
                "median": statistics.median(r.values[name] for r in built),
                "max": max(r.values[name] for r in built),
                "zero_rows": sum(1 for r in built if r.values[name] == 0.0),
            }
            for name in ns.COLUMNS
        },
    }
    print(json.dumps(summary, indent=1))
    return 0


def reconcile_command(args) -> int:
    from collections import defaultdict
    from datetime import datetime

    declaration, auctions, payload, manifest = _auctions()
    records = json.loads(payload.read_text())["data"]
    published = [row for row in load_daily_panel(args.published) if row.date <= END]
    gross = ns.gross_by_day(auctions)
    columns = ("treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons")
    out = {"snapshot_sha256": manifest["sha256"], "gross_vs_panel": {}}
    for name in columns:
        diffs = [(row.date, gross.get(row.date, {}).get(name, 0.0) - float(row.values[name])) for row in published
                 if row.values.get(name) is not None]
        bad = [(d, v) for d, v in diffs if abs(v) > 1e-6]
        out["gross_vs_panel"][name] = {
            "panel_days": len(diffs),
            "days_equal": len(diffs) - len(bad),
            "days_differing": len(bad),
            "max_abs_difference_bn": max((abs(v) for _d, v in diffs), default=0.0),
            "first_differences": [(d.isoformat(), round(v, 6)) for d, v in bad[:10]],
        }
    # SOMA add-ons: the snapshot's against the panel's treasury_settlement_soma.
    soma_by_day = defaultdict(float)
    withheld = set()
    for auction in auctions:
        if auction.soma is None:
            withheld.add(auction.settles)
        else:
            soma_by_day[auction.settles] += auction.soma
    soma_diffs = [
        abs(soma_by_day.get(row.date, 0.0) - float(row.values["treasury_settlement_soma"]))
        for row in published
        if row.values.get("treasury_settlement_soma") is not None and row.date not in withheld
    ]
    out["soma_vs_panel"] = {
        "panel_days": len(soma_diffs),
        "days_differing": sum(1 for v in soma_diffs if v > 1e-6),
        "max_abs_difference_bn": max(soma_diffs, default=0.0),
    }
    # The announced maturing amount against the table's own earlier bill auctions (bills live under a year).
    maturing = defaultdict(float)
    for record in records:
        if record["security_type"] == "Bill" and record["total_accepted"] != "null":
            maturing[record["maturity_date"]] += (
                float(record["total_accepted"]) - float(record["soma_accepted"] or 0)
            ) / 1e9
    ratios = []
    group_maturing = defaultdict(list)
    for auction in auctions:
        if auction.kind == "Bill" and auction.maturing is not None:
            group_maturing[auction.settles].append(auction.maturing)
    for day, figures in group_maturing.items():
        if day >= date(2019, 3, 1) and maturing.get(day.isoformat(), 0) > 0:
            ratios.append(max(figures) / maturing[day.isoformat()])
    out["maturing_vs_earlier_bill_auctions"] = {
        "note": "the announced publicly held maturing figure of a bill settlement day over the sum of (total_accepted - soma_accepted) of the bill auctions in the table that mature that day; settlement days from 2019-03-01 (a bill lives under a year)",
        "days": len(ratios),
        "median_ratio": statistics.median(ratios) if ratios else None,
        "share_within_1pct": sum(1 for r in ratios if abs(r - 1) <= 0.01) / len(ratios) if ratios else None,
        "share_within_5pct": sum(1 for r in ratios if abs(r - 1) <= 0.05) / len(ratios) if ratios else None,
    }
    # Groups of auctions with no maturing figure at all, within the scored span.
    groups = defaultdict(list)
    for auction in auctions:
        if auction.settles <= END:
            groups[(auction.settles, auction.kind)].append(auction)
    unknown = [key for key, members in groups.items() if all(a.maturing is None for a in members)]
    gross_unknown = sum(sum(a.offering for a in groups[key]) for key in unknown)
    gross_all = sum(a.offering for members in groups.values() for a in members)
    out["groups_without_maturing_figure"] = {
        "groups": len(groups),
        "without_figure": len(unknown),
        "gross_bn": gross_unknown,
        "share_of_gross": gross_unknown / gross_all,
        "by_kind": {kind: sum(1 for _d, k in unknown if k == kind) for kind in sorted({k for _d, k in unknown})},
    }
    # What was announced at each decision about the next five days.
    by_day = ns._by_day(auctions)
    shares = []
    for row in published:
        instant = datetime.combine(row.date, time.fromisoformat(declaration["announcement_time"]))
        known = total = 0.0
        current = row.date
        for _ in range(ns.WINDOW_DAYS):
            current = next_business_day(current, 1)
            members = by_day.get(current, ())
            total += sum(a.offering for a in members)
            known += sum(a.offering for a in ns.known_auctions(members, instant))
        if total > 0:
            shares.append(known / total)
    out["announced_share_of_next_five_days_gross"] = {
        "decisions": len(shares),
        "mean": statistics.mean(shares),
        "median": statistics.median(shares),
        "share_of_decisions_fully_announced": sum(1 for s in shares if s >= 1 - 1e-12) / len(shares),
        "share_of_decisions_under_half": sum(1 for s in shares if s < 0.5) / len(shares),
    }
    own = []
    for row in published:
        instant = datetime.combine(row.date, time.fromisoformat(declaration["announcement_time"]))
        members = by_day.get(row.date, ())
        if members:
            own.append(sum(a.offering for a in ns.known_auctions(members, instant)) / sum(a.offering for a in members))
    out["announced_share_of_own_day_gross"] = {
        "settlement_days": len(own),
        "share_fully_announced": sum(1 for s in own if s >= 1 - 1e-12) / len(own),
        "min": min(own),
    }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


def onset_features(horizon: int, net: bool):
    onset = json.loads(ONSET_DECLARATION.read_text())
    spec = onset["candidates"]["onset_logistic"]
    names = [name for group in spec["inputs"] for name in onset["features"][group]]
    features = [name for name in names if horizon == 1 or name != SETTLEMENT]
    return tuple(features + (list(ns.COLUMNS) if net else [])), spec


def hierarchical_features(horizon: int, net: bool):
    return tuple(list(hl.features_at_horizon(horizon)) + (list(ns.COLUMNS) if net else []))


def run_command(args) -> int:
    commit = committed(DECLARATION)
    committed(REPO / "metadata" / "pressure_judge.json")
    require_unlocked([END], where="net_settlement")
    declared = json.loads(DECLARATION.read_text())
    h = args.horizon
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    forecasts, settings = {}, {}

    def backtest(name, predictor, features):
        with switched_on():
            report = rolling_exceedance_backtest(
                rows, predictor=predictor, model_name=name, features=features, registry=registry,
                decision_time=DECISION, taus=taus, minimum_history=MINIMUM_HISTORY,
                refit_every=REFIT_EVERY, end=END, horizon=h,
            )
        forecast = pj.report_forecast(name, pressure.recalibrated(report))
        forecasts[name] = {
            f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
            for tau, column in forecast.probabilities.items()
        }
        settings[name] = {"features": list(report.features), "model_settings": _keyed(dict(report.model_settings))}
        print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)

    for name, net in ((HIERARCHICAL, False), (HIERARCHICAL_NET, True)):
        features = hierarchical_features(h, net)
        predictor = ml._scarcity_calendar_predictor(
            "logistic", features, splits, sc.STATE_FORMS[hl.STATE_FORM],
            minimum_history=MINIMUM_HISTORY, regime_hierarchical=True,
        )
        backtest(name, predictor, features)
    for name, net in ((ONSET, False), (ONSET_NET, True)):
        features, spec = onset_features(h, net)
        predictor = ml.pressure_onset_exceedance(
            spec["kind"], spec["treatment"], features, splits, minimum_history=MINIMUM_HISTORY,
            optional=spec["optional"],
        )
        backtest(name, predictor, features)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.panel),
        "declaration_commit": commit,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


PAIRS = ((HIERARCHICAL_NET, HIERARCHICAL), (ONSET_NET, ONSET))


def pair_command(args) -> int:
    declaration = pj.load_declaration()
    judge_script = _script("pressure_judge")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    out = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        by_name = {f.name: f for f in pj.forecasts_from_horizon_document(document)}
        h = int(document["horizon"])
        states = judge_script._scarcity_states(h, declaration.last_day)
        reference = by_name[HIERARCHICAL]
        grid = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states)
        for with_net, control in PAIRS:
            for tau in declaration.thresholds:
                new, old = by_name[with_net].probabilities[tau], by_name[control].probabilities[tau]
                y = grid.outcomes[tau]
                gain = [(old[i] - y[i]) ** 2 - (new[i] - y[i]) ** 2 for i in range(len(y))]
                cells = {"all": list(range(len(y)))}
                for dimension in ("regime", "day_type"):
                    for label in sorted(set(grid.groups[dimension])):
                        cells[f"{dimension}: {label}"] = [i for i, g in enumerate(grid.groups[dimension]) if g == label]
                for label, members in cells.items():
                    values = [gain[i] for i in members]

                    def statistic(indices, values=values):
                        return sum(values[i] for i in indices) / len(indices)

                    mean = sum(values) / len(values)
                    interval = (
                        stationary_bootstrap_interval(
                            statistic, len(values), block_length=declaration.block_length,
                            seed=declaration.seed + h, replications=declaration.replications, level=declaration.level,
                        )
                        if len(values) > 1 and any(v != 0 for v in values) else (mean, mean)
                    )
                    out.setdefault(with_net, {}).setdefault(f"+{tau:g}", {}).setdefault(str(h), {})[label] = {
                        "days": len(values),
                        "brier_gain_vs_control": mean,
                        "interval": list(interval),
                        "pressure_days": sum(y[i] for i in members),
                    }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for name, taus in out.items():
        for tau, hs in taus.items():
            for h, cells in sorted(hs.items()):
                cell = cells["all"]
                print(f"{name} {tau} h={h}: ΔBrier {cell['brier_gain_vs_control']:+.5f} "
                      f"[{cell['interval'][0]:+.5f}, {cell['interval'][1]:+.5f}]")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(handler=panel_command)
    reconcile = commands.add_parser("reconcile")
    reconcile.add_argument("--panel", type=Path, required=True)
    reconcile.add_argument("--published", type=Path, required=True)
    reconcile.add_argument("--output", type=Path, required=True)
    reconcile.set_defaults(handler=reconcile_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    pair = commands.add_parser("pair")
    pair.add_argument("--panel", type=Path, required=True)
    pair.add_argument("--output", type=Path, required=True)
    pair.add_argument("inputs", nargs="+", type=Path)
    pair.set_defaults(handler=pair_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
