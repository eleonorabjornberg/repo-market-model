#!/usr/bin/env python3
"""Emit the README's Key-findings block and its figure from the run records.

Nothing in the block is typed. Every figure is read out of `docs/runs/*.json` --
the records `backtest`, `compare` and `exceedance-backtest` wrote, each carrying the panel
manifest it was built from and the commit it ran at -- and rendered into
`README.md` between two markers, plus a reliability figure under `docs/figures/`.

**Why this is a generator and not a paragraph.** Milestone A's exit criterion was
that no figure from a run record is transcribed into any Markdown page, and
`tests/test_docs_freshness.py` exists because three documents once published a
test count that had been true months earlier. A results table is the most
decay-prone claim a repository can publish: it is stale the next time anything is
scored. So the table is emitted, the emission is checkable with `--check`, and a
record that changes without the page changing is a red suite rather than a page
nobody re-read.

`notebooks/01_portfolio_walkthrough.ipynb` is generated the same way, from
`examples/walkthrough.py`'s own cells, for the same reason: a notebook committed
beside a script is a second copy, and the copy nobody executes is the one that
rots.

The figure is a reliability diagram per declared threshold, drawn from the CORP
curve and the stationary-bootstrap band already stored in the exceedance record.
Two files are written, light and dark, and `README.md` selects between them with
`<picture>`: GitHub serves the README in both themes, and a single figure legible
in one is illegible in the other. The dark file is stepped for the dark surface,
not colour-flipped.

Standard library only, like the package and like `emit_status.py`.

    python3 scripts/emit_results.py            # rewrites the block and figures
    python3 scripts/emit_results.py --check    # exits 1 on any drift, writes nothing
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "docs/runs"
FIGURES = ROOT / "docs/figures"
README = ROOT / "README.md"
WALKTHROUGH = ROOT / "examples/walkthrough.py"
NOTEBOOK = ROOT / "notebooks/01_portfolio_walkthrough.ipynb"

BEGIN = "<!-- generated: key-findings -->"
END = "<!-- end generated: key-findings -->"
STATUS_BEGIN = "<!-- generated: status -->"
STATUS_END = "<!-- end generated: status -->"
TAIL_BEGIN = "<!-- generated: tail -->"
TAIL_END = "<!-- end generated: tail -->"
HEADLINE_BEGIN = "<!-- generated: headline -->"
HEADLINE_END = "<!-- end generated: headline -->"

PERSISTENCE = "persistence_funding.json"
EXCEEDANCE = "exceedance_climatology.json"
EXCEEDANCE_GBM = "exceedance_gbm.json"

# Chart chrome, light and dark, from the project's data-visualisation palette.
# Both are selected for their own surface rather than one being a flip of the
# other, which is why the series step differs between them.
THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "secondary": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "series": "#2a78d6",
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#ffffff",
        "secondary": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "series": "#3987e5",
    },
}

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


class RecordError(RuntimeError):
    """A run record does not carry what the page needs. Do not guess."""


def load(name):
    path = RUNS / name
    if not path.exists():
        raise RecordError("%s is missing; nothing to publish" % path)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(mapping, *path):
    node = mapping
    for key in path:
        if not isinstance(node, dict) or key not in node:
            raise RecordError("run record has no %s" % ".".join(path))
        node = node[key]
    return node


def bp(value, places=2):
    return ("%." + str(places) + "f") % value


def signed(value, places=3):
    """A skill score with its sign kept: `+0.213`, never `0.213`."""

    return ("%+." + str(places) + "f") % value


def pct(value, places=1):
    return ("%." + str(places) + "f%%") % (value * 100.0)


# --------------------------------------------------------------------------
# the block


def interval_text(entry, places=2, unit=" bp"):
    """`1.23 to 4.56 bp`, or the record's stated reason it has none."""

    if "interval" in entry:
        return "%s to %s%s" % (bp(entry["interval"]["lower"], places),
                               bp(entry["interval"]["upper"], places), unit)
    if "interval_unavailable" in entry:
        return "no interval"
    return "no interval"


def signed_interval(entry, places=2):
    if "interval" not in entry:
        return "no interval"
    return "%s to %s" % (signed(entry["interval"]["lower"], places),
                         signed(entry["interval"]["upper"], places))


def verdict(lower, upper, better, worse):
    if lower > 0:
        return better
    if upper < 0:
        return worse
    return "not distinguishable"


def split_table(splits, key, labels, value_header, places=2, signed_values=False):
    """One split of one series as a Markdown table, every declared group listed."""

    groups = require(splits, key)
    lines = ["| %s | Days | %s | 90%% interval |" % (labels, value_header),
             "|---|---|---|---|"]
    for name, entry in groups.items():
        if not entry["count"]:
            lines.append("| %s | 0 | no day | |" % name.replace("_", " "))
            continue
        mean = signed(entry["mean"], places) if signed_values else bp(entry["mean"], places)
        span = (signed_interval(entry, places) if signed_values
                else interval_text(entry, places, ""))
        lines.append("| %s | %d | %s | %s |" % (name.replace("_", " "), entry["count"],
                                                mean, span))
    return lines


def split_matrix(rows, key, places=2):
    """Several series' splits side by side: one row per series, one column per group."""

    groups = list(require(rows[0][1], key))
    lines = ["| | %s |" % " | ".join(name.replace("_", " ") for name in groups),
             "|---|" + "---|" * len(groups)]
    for label, splits in rows:
        cells = []
        for name in groups:
            entry = require(splits, key, name)
            if not entry["count"]:
                cells.append("no day")
            else:
                cells.append("%s (%s)" % (signed(entry["mean"], places),
                                          signed_interval(entry, places)))
        lines.append("| %s | %s |" % (label, " | ".join(cells)))
    return lines


def information_sentence(record):
    """Where the target was read, from the record's own information-set summary."""

    target = require(record, "derived", "information_set", "features", "spread_bps")
    rows = require(target, "rows_before_scored")
    if len(rows) == 1:
        (gap, days), = rows.items()
        return ("the spread itself is read %s panel rows before the scored day, on all %d "
                "scored days" % (gap, days))
    return ("the spread itself is read %s panel rows before the scored day, by day"
            % ", ".join("%s (%d days)" % item for item in sorted(rows.items())))


def key_findings(persistence, exceedance, conditional):
    panel = require(persistence, "panel")
    folds = require(persistence, "folds")
    metrics = require(persistence, "metrics")
    interval = require(metrics, "mae_bps_interval")
    coverage = require(metrics, "interval_calibration", "coverage_interval")
    nominal = require(metrics, "interval_calibration", "declared_probability")
    pinball = require(metrics, "pinball_loss")
    taus = require(exceedance, "metrics", "by_tau")
    commit = require(persistence, "provenance", "code", "commit")[:7]
    refit = require(persistence, "declaration", "refit_every")

    levels = sorted(pinball, key=float)
    skills = sorted(taus, key=float)
    worst_skill = max(abs(taus[key]["brier_skill_score"]) for key in skills)

    lines = []
    add = lines.append
    add(BEGIN)
    add("<!-- Generated by scripts/emit_results.py from docs/runs/. Do not edit by hand:")
    add("     the block is regenerated from the run records and checked in the suite. -->")
    add("")
    add("Every figure here is scored under the as-of information rule")
    add("(`docs/decisions/information-set.md`). The records scored under the earlier purge")
    add("rule are archived in `docs/runs/archive/pre-asof/` (`docs/pivot/lag-assessment.md` §4).")
    add("Phase 2's verdict, made again on these as-of records, is in `PLAN.md`.")
    add("")
    add("**Target.** The next-business-day value of the panel field `spread_bps` — the SOFR")
    add("to IORB spread in basis points — forecast at %s on the previous business day from"
        % require(persistence, "declaration", "decision_time"))
    add("each input's latest value public at that instant: %s." % information_sentence(persistence))
    add("")
    add("**Panel.** %s to %s, %d rows, SHA-256 `%s`." % (
        panel["first_date"], panel["last_date"], panel["row_count"], panel["sha256"][:12]))
    add("")
    add("**Evaluation.** As-of rolling origin, refitted every %d scored days, **%d forecast"
        % (refit, folds["count"]))
    add("origins**, first scored %s, last scored %s. Run at `%s`."
        % (folds["first"]["scored_date"], folds["last"]["scored_date"], commit))
    add("")
    add("| Measure | Benchmark | Value | 90% interval |")
    add("|---|---|---|---|")
    add("| Mean absolute error | persistence | %s bp | %s to %s bp |" % (
        bp(metrics["mae_bps"]), bp(interval["lower"]), bp(interval["upper"])))
    add("| CRPS | persistence | %s bp | not intervalled |" % bp(metrics["crps_bps"]))
    add("| Interval coverage | nominal %s | **%s** | %s to %s |" % (
        pct(metrics["interval_probability"], 0), pct(metrics["interval_coverage"]),
        pct(coverage["lower"]), pct(coverage["upper"])))
    for level in levels:
        add("| Pinball loss, quantile %s | persistence | %s bp | not intervalled |" % (
            level, bp(pinball[level])))
    add("")
    add("The interval is a stationary bootstrap, block length %d, %d replications, "
        "on the errors themselves; the folds overlap in horizon, so a formula assuming "
        "independent draws would report a narrower interval than the data supports."
        % (interval["block_length"], interval["replications"]))
    add("")
    excludes = not (coverage["lower"] <= nominal <= coverage["upper"])
    add("**Persistence's coverage %s.** A nominal %s interval covered %s of %d realised "
        "outcomes; intervalled the same way as the error above (seed %d), the realised "
        "coverage lies between %s and %s, which %s the nominal probability."
        % ("is a calibration finding" if excludes else "is not a calibration finding",
           pct(metrics["interval_probability"], 0), pct(metrics["interval_coverage"]),
           folds["count"], coverage["seed"], pct(coverage["lower"]), pct(coverage["upper"]),
           "excludes" if excludes else "includes"))
    add("")
    splits = require(metrics, "mae_bps_splits")
    add("**Persistence by regime and by pressure-day type.** The same errors, split as "
        "`metadata/evaluation_splits.json` declares (status: %s). Each interval resamples "
        "the whole series with the pooled interval's block length and seed, and averages "
        "the resampled days of the group."
        % require(persistence, "splits", "declaration", "status").split(":")[0])
    add("")
    lines.extend(split_table(splits, "by_regime", "Regime", "Mean absolute error"))
    add("")
    lines.extend(split_table(splits, "by_day_type", "Pressure-day type", "Mean absolute error"))
    add("")
    table, challengers = challenger_section()
    lines.extend(table)
    add("")
    add("**The paired difference by regime and by pressure-day type** (persistence's CRPS "
        "minus the challenger's, bp, with its 90% interval):")
    add("")
    split_rows = [(label, require(record, "comparison", "splits"))
                  for label, record in challengers]
    lines.extend(split_matrix(split_rows, "by_regime"))
    add("")
    lines.extend(split_matrix(split_rows, "by_day_type"))
    add("")
    add("**Interval coverage on the same origins.**")
    add("")
    lines.extend(coverage_section(challengers, persistence))
    add("")
    lines.extend(pressure_section())
    add("")
    add("**The control that licenses every skill number.** A climatology scored "
        "against climatology must show no skill. Over the same %d origins its Brier "
        "skill score is %s at every declared threshold (%s bp), and its reference Brier "
        "score equals its own at each one."
        % (require(exceedance, "metrics", "scored_days"),
           bp(worst_skill, 3),
           ", ".join(str(int(float(key))) for key in skills)))
    add("")
    add("<picture>")
    add('  <source media="(prefers-color-scheme: dark)" '
        'srcset="docs/figures/reliability-dark.svg">')
    add('  <img alt="Reliability of the exceedance forecasts at each declared threshold" '
        'src="docs/figures/reliability.svg">')
    add("</picture>")
    add("")
    add("CORP reliability curves with %s%% stationary-bootstrap bands, one panel per "
        "declared stress threshold. The diagonal is perfect calibration; the base rate "
        "under each panel is how often the threshold was actually exceeded."
        % bp(require(taus[skills[0]], "reliability_curve", "band", "level") * 100, 0))
    add("")
    add(END)
    return "\n".join(lines)


# --------------------------------------------------------------------------
# the pressure probability against its two benchmarks

PRESSURE = "exceedance_*.json"
#: The thresholds the pressure-probability headline is stated at
#: (`docs/decisions/pressure-probability.md`): P(spread >= 5 bp) and >= 10 bp.
HEADLINE_TAUS = ("5", "10")
BENCHMARK_LABELS = (
    ("calendar_climatology", "calendar-type climatology"),
    ("persistence_logistic", "persistence-logistic"),
)


def pressure_records():
    """Every exceedance record, labelled by its declared model and settings."""

    found = []
    for path in sorted(RUNS.glob(PRESSURE)):
        with path.open(encoding="utf-8") as handle:
            record = json.load(handle)
        declaration = require(record, "declaration")
        label = _settings(declaration).replace(
            "calendar_climatology", "calendar-type climatology").replace(
            "persistence_logistic", "persistence-logistic")
        if declaration["model"] == "gbm":
            label += " on %s" % ", ".join("`%s`" % f for f in declaration["features"])
        found.append((label, record))
    if not found:
        raise RecordError("no %s record in docs/runs/" % PRESSURE)
    keys = set(_Scored.key(record) for _, record in found)
    if len(keys) != 1:
        raise RecordError("exceedance records are not scored on one panel, history, "
                          "refit and origin count: %s" % sorted(keys))
    return found


def pressure_section():
    records = pressure_records()
    lines = []
    add = lines.append
    first = records[0][1]
    add("**The pressure probability against its two benchmarks.** Every exceedance record "
        "is scored on the same %d days; the event is the spread strictly above the "
        "threshold on the scored day (`metadata/stress_thresholds.json`). The benchmarks "
        "are those of `docs/decisions/pressure-probability.md`: a calendar-type "
        "climatology and a persistence-logistic model, each scored in the same run under "
        "its own declaration and paired with the model day by day. The difference is the "
        "benchmark's Brier score minus the model's, so a positive value favours the "
        "model; its interval is a stationary bootstrap on the per-day differences. "
        "Average precision is the area under the precision-recall curve, against a "
        "no-skill value equal to the base rate."
        % require(first, "metrics", "scored_days"))
    add("")
    for key in HEADLINE_TAUS:
        row = require(first, "metrics", "by_tau", key)
        add("*Threshold %g bp, exceeded on %s of days.*" % (row["tau_bp"], pct(row["base_rate"])))
        add("")
        add("| Model | Brier | Average precision | vs calendar-type climatology | "
            "vs persistence-logistic |")
        add("|---|---|---|---|---|")
        for label, record in records:
            entry = require(record, "metrics", "by_tau", key)
            cells = []
            for name, _ in BENCHMARK_LABELS:
                bench = record.get("benchmarks", {}).get(name)
                if bench is None:
                    cells.append("—")
                    continue
                paired = require(bench, "by_tau", key, "paired_brier_difference")
                cells.append("%s (%s), %s" % (
                    signed(paired["mean"], 4),
                    "%s to %s" % (signed(paired["interval"]["lower"], 4),
                                  signed(paired["interval"]["upper"], 4)),
                    verdict(paired["interval"]["lower"], paired["interval"]["upper"],
                            "beats it", "loses to it")))
            ap = entry.get("average_precision")
            add("| %s | %s | %s | %s | %s |" % (
                label, bp(entry["brier"], 4), "—" if ap is None else bp(ap, 3),
                cells[0], cells[1]))
        add("")
    add("**The paired Brier difference against the persistence-logistic, %g bp, by regime "
        "and by pressure-day type** (benchmark minus model, with its 90%% interval):"
        % float(HEADLINE_TAUS[0]))
    add("")
    split_rows = []
    for label, record in records:
        bench = record.get("benchmarks", {}).get("persistence_logistic")
        if bench is None:
            continue
        split_rows.append((label, require(bench, "by_tau", HEADLINE_TAUS[0],
                                          "paired_brier_difference", "splits")))
    if split_rows:
        lines.extend(split_matrix(split_rows, "by_regime", 4))
        add("")
        lines.extend(split_matrix(split_rows, "by_day_type", 4))
    return lines


def tail_section(conditional):
    """Phase 2's tail clause, as the run record measured it.

    Every number here is read off `docs/runs/exceedance_gbm_mh61.json`. Where the
    record declares a metric unavailable it says why, and this block quotes that
    reason rather than substituting a number of its own: a clipped log score is a
    finite loss chosen by whoever picked the clip, standing in for the failure that
    is the finding.
    """

    taus = require(conditional, "metrics", "by_tau")
    order = sorted(taus, key=float)
    scored = require(conditional, "metrics", "scored_days")
    refit = require(conditional, "declaration", "refit_every")
    commit = require(conditional, "provenance", "code", "commit")[:7]

    lines = []
    add = lines.append
    add(TAIL_BEGIN)
    add("<!-- Generated by scripts/emit_results.py from docs/runs/. Do not edit by hand:")
    add("     the block is regenerated from the run record and checked in the suite. -->")
    add("")
    add("The conditional model's exceedance probabilities, scored over %d days under "
        "the as-of rule, refitted every %d scored days, against a climatology refitted "
        "on each fit's training rows. Run at `%s`." % (scored, refit, commit))
    add("")
    add("| Threshold | Exceeded on | Brier skill vs climatology | 90% interval | "
        "Discrimination realised |")
    add("|---|---|---|---|---|")
    for key in order:
        entry = taus[key]
        interval = require(entry, "brier_skill_score_interval")
        decomposition = require(entry, "decomposition")
        add("| \u03c4 = %g bp | %s of days | **%s** | %s to %s | %s |" % (
            entry["tau_bp"], pct(entry["base_rate"]),
            signed(entry["brier_skill_score"]),
            signed(interval["lower"]), signed(interval["upper"]),
            pct(realized_discrimination(decomposition), 2)))
    add("")
    # Which thresholds are findings is computed: an interval that excludes zero is one.
    beats = [taus[key] for key in order
             if require(taus[key], "brier_skill_score_interval")["lower"] > 0]
    loses = [taus[key] for key in order
             if require(taus[key], "brier_skill_score_interval")["upper"] < 0]
    add("**Where the skill is.** The skill interval excludes zero "
        "above climatology at %s, and below it at %s. The last column is resolution as a "
        "share of uncertainty -- how much of the discrimination a sample had available "
        "the forecasts actually realised. It is the honest form of the comparison, "
        "because resolution and uncertainty both collapse as the event gets rarer and "
        "a resolution quoted alone cannot tell a model that stopped discriminating "
        "from a sample with nothing left to discriminate. It falls from %s at %g bp to "
        "%s at %g bp."
        % (thresholds(beats), thresholds(loses),
           pct(realized_discrimination(require(taus[order[0]], "decomposition")), 2),
           taus[order[0]]["tau_bp"],
           pct(realized_discrimination(require(taus[order[-1]], "decomposition")), 2),
           taus[order[-1]]["tau_bp"]))
    add("")
    for key in order:
        entry = taus[key]
        for metric, reason in sorted(entry.get("unavailable", {}).items()):
            text = reason.rstrip(".")
            add("**At %g bp the record reports no %s.** %s."
                % (entry["tau_bp"], metric.replace("_", " "),
                   text[:1].upper() + text[1:]))
            add("")
    add("<picture>")
    add('  <source media="(prefers-color-scheme: dark)" '
        'srcset="docs/figures/reliability-gbm-dark.svg">')
    add('  <img alt="Reliability of the conditional model\'s exceedance forecasts at '
        'each declared threshold" src="docs/figures/reliability-gbm.svg">')
    add("</picture>")
    add("")
    add("The same CORP reliability curves for the conditional model, beside the "
        "climatology control above.")
    add("")
    add(TAIL_END)
    return "\n".join(lines)


def realized_discrimination(decomposition):
    """Resolution as a share of uncertainty, from the record's own two terms.

    `metrics.CorpDecomposition` computes this at scoring time and
    `baseline._decomposition_document` now writes it, but the **published records
    in `docs/runs/` predate the field** and will not carry it until they are
    re-scored, which is a human's call. So this derives it from the two terms
    those records do carry, rather than transcribing it from anywhere.

    The trigger for deleting this is therefore the records, not the writer: once
    every record this generator reads carries `realized_discrimination`, read the
    field and delete this function. Deleting it while a record on disk lacks the
    field would raise `RecordError` on a page that is otherwise fine.
    """

    uncertainty = require(decomposition, "uncertainty")
    if not uncertainty:
        raise RecordError("a decomposition with no uncertainty carries no share")
    return require(decomposition, "resolution") / uncertainty


def thresholds(entries):
    """`5 bp`, or `5 and 10 bp`, or `none` -- never an empty phrase."""

    if not entries:
        return "no declared threshold"
    labels = ["%g" % entry["tau_bp"] for entry in entries]
    if len(labels) == 1:
        return "%s bp" % labels[0]
    return "%s and %s bp" % (", ".join(labels[:-1]), labels[-1])


# --------------------------------------------------------------------------
# challengers and interval coverage

CHALLENGERS = "compare_persistence_vs_*_crps.json"
COVERAGE = "backtest_*.json"


class _Scored(object):
    """What a challenger or coverage record was scored on, compared as a key.

    Every row of a generated table must share the origins, panel, refit cadence
    and history it was scored on, or the table ranks numbers that are not
    comparable. A record that differs is refused, never quietly left out.
    """

    @staticmethod
    def key(record):
        return (
            require(record, "panel", "sha256"),
            require(record, "declaration", "minimum_history"),
            require(record, "declaration", "refit_every"),
            require(record, "folds", "count"),
        )


#: Declaration keys that are not model settings: shared by every row of a
#: table (and checked to be), so showing them would repeat them per row.
_NOT_SETTINGS = ("model", "features", "decision_time", "minimum_history", "refit_every",
                 "taus_bp", "twcrps_weights")


def _settings(side):
    """A declared model side as a label: its name, then each declared setting.

    Since B21 a declaration names `regime_variable` / `residual_window`; any
    key other than `model` and `features` is a setting and is shown.
    """

    extra = ["%s `%s`" % (key.replace("_", " "), side[key])
             for key in sorted(side) if key not in _NOT_SETTINGS]
    return side["model"] + (" (%s)" % ", ".join(extra) if extra else "")


def challenger_records():
    """The CRPS comparisons against persistence, labelled and checked."""

    found = []
    for path in sorted(RUNS.glob(CHALLENGERS)):
        with path.open(encoding="utf-8") as handle:
            record = json.load(handle)
        if require(record, "comparison", "model_a", "model") != "persistence":
            raise RecordError("%s does not compare against persistence" % path.name)
        found.append(record)
    if not found:
        raise RecordError("no %s record in docs/runs/; nothing to rank" % CHALLENGERS)
    keys = set(_Scored.key(record) for record in found)
    if len(keys) != 1:
        raise RecordError("challenger records are not scored on one panel, history, "
                          "refit and origin count: %s" % sorted(keys))

    labels = [_settings(require(r, "declaration", "model_b")) for r in found]
    # A gbm is named with its features: the published set scores one model on two
    # declarations.
    labels = [
        label + (" on %s" % ", ".join("`%s`" % f for f in r["declaration"]["model_b"]["features"])
                 if r["declaration"]["model_b"]["model"] == "gbm" else "")
        for label, r in zip(labels, found)
    ]
    # Two records whose declared settings agree are told apart by the features
    # they alone use -- the ARX pair differ only in their exogenous columns.
    for label in set(labels):
        group = [i for i, value in enumerate(labels) if value == label]
        if len(group) < 2:
            continue
        sets = [set(require(found[i], "declaration", "model_b", "features")) for i in group]
        shared = set.intersection(*sets)
        for i, features in zip(group, sets):
            own = sorted(features - shared)
            if not own:
                raise RecordError("two challenger records declare the same model, "
                                  "settings and features: %s" % label)
            labels[i] = "%s with %s" % (label, ", ".join("`%s`" % f for f in own))
    return sorted(zip(labels, found),
                  key=lambda pair: -pair[1]["comparison"]["mean_difference_bps"])


def challenger_section():
    rows = challenger_records()
    first = rows[0][1]
    comparison = first["comparison"]
    lines = []
    add = lines.append
    add("**Challengers against persistence.** Each challenger is scored on the same "
        "%d origins (minimum history %d, refitted every %d scored days); persistence's "
        "CRPS is %s bp. "
        "The difference is persistence's CRPS minus the challenger's, so a positive "
        "value favours the challenger; its interval is a stationary bootstrap "
        "(block length %d, %d replications) on the per-origin differences."
        % (comparison["origin_count"], first["declaration"]["minimum_history"],
           first["declaration"]["refit_every"], bp(comparison["model_a"]["crps_bps"]),
           comparison["mean_difference_interval"]["block_length"],
           comparison["mean_difference_interval"]["replications"]))
    add("")
    add("| Challenger | CRPS | Difference | 90% interval | Verdict |")
    add("|---|---|---|---|---|")
    for label, record in rows:
        c = record["comparison"]
        interval = c["mean_difference_interval"]
        if interval["lower"] > 0:
            verdict = "beats persistence"
        elif interval["upper"] < 0:
            verdict = "loses to persistence"
        else:
            verdict = "not distinguishable"
        add("| %s | %s bp | %+.2f bp | %+.2f to %+.2f bp | %s |" % (
            label, bp(c["model_b"]["crps_bps"]), c["mean_difference_bps"],
            interval["lower"], interval["upper"], verdict))
    return lines, rows


def coverage_section(challengers, persistence):
    """Interval coverage of every backtest scored on the challengers' origins.

    The persistence record is `persistence_funding.json`, not a `backtest_*`
    file, and is listed beside them when it shares their origins.
    """

    reference = _Scored.key(challengers[0][1])
    found = [persistence] if _Scored.key(persistence) == reference else []
    for path in sorted(RUNS.glob(COVERAGE)):
        with path.open(encoding="utf-8") as handle:
            record = json.load(handle)
        if _Scored.key(record) == reference:
            found.append(record)
    if not found:
        raise RecordError("no backtest record shares the challengers' origins; "
                          "interval coverage cannot be published beside them")
    lines = []
    add = lines.append
    top = max(float(level) for level in require(found[0], "metrics", "pinball_loss"))
    add("| Model | Nominal | Realised coverage | 90%% interval | Pinball loss, quantile %.2f |"
        % top)
    add("|---|---|---|---|---|")
    verdicts = []
    for record in sorted(found, key=lambda r: (r["declaration"]["model"],
                                               len(r["declaration"]["features"]),
                                               r["declaration"].get("calibration", ""))):
        metrics = require(record, "metrics")
        calibration = require(metrics, "interval_calibration")
        interval = require(calibration, "coverage_interval")
        nominal = require(calibration, "declared_probability")
        pinball = require(metrics, "pinball_loss")
        level = [key for key in pinball if float(key) == top][0]
        model = _settings(require(record, "declaration"))
        if record["declaration"]["model"] == "gbm":
            model += " on %s" % ", ".join("`%s`" % f for f in record["declaration"]["features"])
        add("| %s | %s | %s | %s to %s | %s bp |" % (
            model, pct(nominal, 0), pct(calibration["realized_coverage"]),
            pct(interval["lower"]), pct(interval["upper"]), bp(pinball[level], 3)))
        if not (interval["lower"] <= nominal <= interval["upper"]):
            verdicts.append(model)
    add("")
    add("A realised-coverage interval that excludes the nominal probability is a "
        "calibration finding. %s" % (
            "It is one for: %s." % ", ".join(verdicts) if verdicts
            else "None of these models has one."))
    return lines


def status_line():
    """The current phase, read from PLAN.md through `emit_status.py`'s parser.

    Deliberately **not** read from `docs/status.json`, which was the first
    attempt. That file is regenerated and committed by CI on every push, and it
    carries the head commit, so a block derived from it would differ from itself
    after every unrelated commit and the guard beside this generator would go red
    on `main` for no reason anyone could act on. A guard that cries wolf is
    removed within the month.

    PLAN.md is the source `status.json` itself is generated from, so reading it
    directly puts one source behind both. The consequence is intended: editing a
    phase heading in PLAN.md turns the suite red until this block is
    regenerated, which is the same stop-and-report a closed published limitation
    already triggers.
    """

    spec = importlib.util.spec_from_file_location(
        "emit_status", ROOT / "scripts/emit_status.py")
    emit_status = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(emit_status)

    phases = emit_status.parse_plan((ROOT / "PLAN.md").read_text(encoding="utf-8"))
    number, state = emit_status.current_phase(phases)
    phase = phases[number]
    following = phases[number + 1] if number + 1 < len(phases) else phase

    lines = [STATUS_BEGIN]
    lines.append("<!-- Generated by scripts/emit_results.py from PLAN.md. -->")
    lines.append("")
    still_open = "".join(
        ", with phase %d, %s, still open alongside it" % (item["number"], item["name"])
        for item in emit_status.alongside(phases, number))
    lines.append("**Where this is: phase %d of %d — %s (%s)%s.** Its exit criterion is "
                 "%s. Next is phase %d, %s. The machine-readable version is "
                 "[`docs/status.json`](docs/status.json), regenerated in CI from the "
                 "same headings rather than edited."
                 % (phase["number"], len(phases) - 1, phase["name"], state, still_open,
                    emit_status.require_exit(phase, "the current phase"),
                    following["number"], following["name"]))
    lines.append("")
    lines.append(STATUS_END)
    return "\n".join(lines)


def headline(persistence, exceedance):
    """The same figures as the results table, in sentences and without jargon.

    The README's plain-words block, once `docs/EXECUTIVE_SUMMARY.md`, is written
    for someone who will not open a run record, and the temptation there is to round a number into a claim. It is
    generated for exactly that reason: the page a non-technical reader trusts
    most is the page furthest from the evidence, so it gets the same wiring as
    the table and none of the licence.
    """

    metrics = require(persistence, "metrics")
    interval = require(metrics, "mae_bps_interval")
    coverage = require(metrics, "interval_calibration", "coverage_interval")
    nominal = require(metrics, "interval_calibration", "declared_probability")
    folds = require(persistence, "folds")
    panel = require(persistence, "panel")
    taus = require(exceedance, "metrics", "by_tau")
    worst = max(abs(taus[key]["brier_skill_score"]) for key in taus)

    if coverage["upper"] < nominal:
        bands = ("Its uncertainty bands are **too narrow**: a band meant to contain the "
                 "outcome %s of the time contained it %s of the time, and resampling the "
                 "same history does not reach %s.")
    elif coverage["lower"] > nominal:
        bands = ("Its uncertainty bands are **too wide**: a band meant to contain the "
                 "outcome %s of the time contained it %s of the time, and resampling the "
                 "same history does not come down to %s.")
    else:
        bands = ("Its uncertainty bands are about right: a band meant to contain the "
                 "outcome %s of the time contained it %s of the time, within what "
                 "resampling the same history produces around %s.")

    lines = [HEADLINE_BEGIN]
    lines.append("<!-- Generated by scripts/emit_results.py from docs/runs/. -->")
    lines.append("")
    lines.append("- The forecasting machinery has been run end to end on real market data "
                 "covering %s to %s, and scored at **%d separate decision points** — each "
                 "one made only from the latest information already public at 4 pm the "
                 "day before."
                 % (panel["first_date"], panel["last_date"], folds["count"]))
    lines.append("- On that history, a simple benchmark — the latest public value, carried "
                 "forward — is "
                 "wrong by **%s basis points on average**, and the range that error could "
                 "plausibly take is %s to %s basis points."
                 % (bp(metrics["mae_bps"]), bp(interval["lower"]), bp(interval["upper"])))
    lines.append("- " + bands % (pct(nominal, 0), pct(metrics["interval_coverage"]),
                                 pct(nominal, 0)))
    lines.append("- The scoring itself has been checked against a case where the right "
                 "answer is known in advance: a forecast with no information in it scores "
                 "**%s skill**, exactly as it must. Every later claim of skill rests on "
                 "that." % bp(worst, 3))
    lines.append("")
    lines.append("**Every result below is paired against its benchmark and split by regime "
                 "and by type of day.** Phase 2's verdict on these records is in "
                 "[`PLAN.md`](PLAN.md). Nothing here is a basis for a decision about money.")
    lines.append("")
    lines.append(HEADLINE_END)
    return "\n".join(lines)


# --------------------------------------------------------------------------
# the figure


def curve_points(entry):
    """The CORP curve, reduced to the vertices that change it.

    An isotonic curve over 2080 days is a step function stored as one point per
    day. Keeping every one of them would put two thousand near-identical
    coordinates in a file a reader loads to look at a picture; keeping only the
    vertices where the fitted value moves draws the identical line.
    """

    points = require(entry, "reliability_curve", "points")
    kept = []
    for point in sorted(points, key=lambda item: item["forecast"]):
        row = (point["forecast"], point["recalibrated"], point["lower"], point["upper"])
        if not kept or any(abs(a - b) > 1e-9 for a, b in zip(row[1:], kept[-1][1:])):
            kept.append(row)
        else:
            kept[-1] = row
    return kept


def nice_limit(top):
    """A round axis maximum at or above `top`: 1, 2, 2.5 or 5 times a power of ten.

    Written out because the obvious shortcut -- step doubling from a fixed
    starting magnitude -- silently produced a 122% axis on a panel whose data
    stops at 8%, and the figure looked like an empty box with a line in one
    corner. An axis a reader cannot name the ticks of is a broken axis.
    """

    if top <= 0:
        return 1.0
    exponent = math.floor(math.log10(top))
    fraction = top / (10 ** exponent)
    for candidate in (1.0, 2.0, 2.5, 5.0, 10.0):
        if fraction <= candidate + 1e-12:
            return candidate * (10 ** exponent)
    return 10.0 ** (exponent + 1)


def tick_label(value):
    text = "%.3f" % (value * 100.0)
    text = text.rstrip("0").rstrip(".")
    return (text or "0") + "%"


SIDE = 160          # the plot is square, so perfect calibration is the 45 degree line
PAD_LEFT = 46
PAD_RIGHT = 14
PAD_TOP = 30
PAD_BOTTOM = 36
CELL_W = PAD_LEFT + SIDE + PAD_RIGHT
CELL_H = PAD_TOP + SIDE + PAD_BOTTOM


def panel_svg(entry, theme, x0, y0, label, index):
    colors = THEMES[theme]
    points = curve_points(entry)
    # The axis is set by the range of the forecasts themselves, and both axes get
    # the same one so that perfect calibration is the 45 degree line. Neither the
    # bootstrap band nor the fitted curve is allowed to set it: an isotonic fit
    # reaches 1.0 in its top bin, and letting that decide the scale compresses
    # every panel's forecast range into its bottom corner. Both are clipped, so a
    # curve leaving the top of a panel is visible as exactly that.
    top = max(max(p[0] for p in points), 1e-9)
    limit = nice_limit(top)

    px = lambda v: x0 + PAD_LEFT + (v / limit) * SIDE
    py = lambda v: y0 + PAD_TOP + SIDE - (v / limit) * SIDE
    clip = "clip%s%d" % (theme[0], index)

    out = []
    out.append('<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%d" height="%d"/></clipPath>'
               % (clip, px(0), py(limit), SIDE, SIDE))
    out.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="600" fill="%s">%s</text>'
               % (x0 + PAD_LEFT, y0 + 16, colors["ink"], label))
    for fraction in (0.5, 1.0):
        value = limit * fraction
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                   % (px(0), py(value), px(limit), py(value), colors["grid"]))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                   % (px(value), py(0), px(value), py(limit), colors["grid"]))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5" '
               'stroke-dasharray="4 3"/>'
               % (px(0), py(0), px(limit), py(limit), colors["muted"]))
    upper = " ".join("%.1f,%.1f" % (px(p[0]), py(p[3])) for p in points)
    lower = " ".join("%.1f,%.1f" % (px(p[0]), py(p[2])) for p in reversed(points))
    out.append('<polygon clip-path="url(#%s)" points="%s %s" fill="%s" fill-opacity="0.18"/>'
               % (clip, upper, lower, colors["series"]))
    line = " ".join("%.1f,%.1f" % (px(p[0]), py(p[1])) for p in points)
    out.append('<polyline clip-path="url(#%s)" points="%s" fill="none" stroke="%s" '
               'stroke-width="2" stroke-linejoin="round"/>' % (clip, line, colors["series"]))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
               % (px(0), py(0), px(limit), py(0), colors["axis"]))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
               % (px(0), py(0), px(0), py(limit), colors["axis"]))
    for value in (0.0, limit):
        out.append('<text x="%.1f" y="%.1f" font-size="10" text-anchor="middle" fill="%s">%s</text>'
                   % (px(value), py(0) + 13, colors["muted"], tick_label(value)))
        out.append('<text x="%.1f" y="%.1f" font-size="10" text-anchor="end" fill="%s">%s</text>'
                   % (px(0) - 5, py(value) + 3.5, colors["muted"], tick_label(value)))
    out.append('<text x="%.1f" y="%.1f" font-size="10" fill="%s">exceeded on %s of days</text>'
               % (x0 + PAD_LEFT, y0 + CELL_H - 8, colors["secondary"], pct(entry["base_rate"])))
    return out


def figure_svg(exceedance, theme, title="Reliability of the exceedance forecasts"):
    colors = THEMES[theme]
    taus = require(exceedance, "metrics", "by_tau")
    order = sorted(taus, key=float)
    cols = 2
    rows = (len(order) + cols - 1) // cols
    width = cols * CELL_W + 16
    height = rows * CELL_H + 52

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
           'height="%d" font-family=\'%s\' role="img" '
           'aria-label="%s at each declared threshold">'
           % (width, height, width, height, FONT, title)]
    out.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, colors["surface"]))
    out.append('<text x="8" y="20" font-size="13" font-weight="600" fill="%s">'
               '%s</text>' % (colors["ink"], title))
    out.append('<text x="8" y="37" font-size="11" fill="%s">Forecast probability across, '
               'observed frequency up; dashed is perfect calibration</text>'
               % colors["secondary"])
    for index, key in enumerate(order):
        x0 = 8 + (index % cols) * CELL_W
        y0 = 46 + (index // cols) * CELL_H
        out.extend(panel_svg(taus[key], theme, x0, y0,
                             "\u03c4 = %g bp" % taus[key]["tau_bp"], index))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# the notebook


def notebook(source):
    """`examples/walkthrough.py`, cell for cell, as a notebook.

    A notebook checked in beside a script is two copies of one thing, and the
    copy nobody executes is the one that rots -- the same shape as a transcribed
    figure. So the script is the original, its `# %%` markers are the cell
    boundaries, and this renders the notebook from them. Outputs are never
    stored: a committed output is a result nobody re-ran.

    Everything above the first marker -- the shebang and the module docstring --
    is deliberately dropped. It addresses a reader running the script, and the
    notebook says the equivalent in its own first cell.
    """

    cells = []
    kind, body = None, []

    def flush():
        if kind is None:
            return
        text = "\n".join(body).strip("\n")
        if not text.strip():
            return
        if kind == "markdown":
            lines = [line[2:] if line.startswith("# ") else line.lstrip("#")
                     for line in text.splitlines()]
            cells.append({"cell_type": "markdown", "metadata": {},
                          "source": _source(lines)})
        else:
            cells.append({"cell_type": "code", "execution_count": None,
                          "metadata": {}, "outputs": [],
                          "source": _source(text.splitlines())})

    for line in source.splitlines():
        if line.startswith("# %%"):
            flush()
            kind = "markdown" if "[markdown]" in line else "code"
            body = []
            continue
        if kind is not None:
            body.append(line)
    flush()

    document = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        # 4, not 5: minor 5 requires a per-cell id, and an id generated at
        # emission time would make this file differ from itself on every run,
        # which is exactly the drift --check exists to detect.
        "nbformat_minor": 4,
    }
    return json.dumps(document, indent=1, sort_keys=True) + "\n"


def _source(lines):
    """Notebook source: one string per line, newline kept except on the last."""

    while lines and not lines[-1].strip():
        lines.pop()
    return [line + "\n" for line in lines[:-1]] + lines[-1:] if lines else []


# --------------------------------------------------------------------------


CONDITIONAL_TITLE = "Reliability of the conditional model's exceedance forecasts"


def rendered(persistence, exceedance, conditional):
    """Every artifact this script owns, as {path: text}."""

    artifacts = {
        FIGURES / "reliability.svg": figure_svg(exceedance, "light"),
        FIGURES / "reliability-dark.svg": figure_svg(exceedance, "dark"),
        FIGURES / "reliability-gbm.svg": figure_svg(conditional, "light", CONDITIONAL_TITLE),
        FIGURES / "reliability-gbm-dark.svg": figure_svg(conditional, "dark",
                                                         CONDITIONAL_TITLE),
        NOTEBOOK: notebook(WALKTHROUGH.read_text(encoding="utf-8")),
    }
    pages = {
        README: (
            (BEGIN, END, key_findings(persistence, exceedance, conditional)),
            (TAIL_BEGIN, TAIL_END, tail_section(conditional)),
            (STATUS_BEGIN, STATUS_END, status_line()),
            (HEADLINE_BEGIN, HEADLINE_END, headline(persistence, exceedance)),
        ),
    }
    for page, blocks in pages.items():
        if not page.exists():
            raise RecordError("%s is missing; this script fills blocks in pages "
                              "rather than writing them" % page)
        text = page.read_text(encoding="utf-8")
        for begin, end, block in blocks:
            start = text.find(begin)
            finish = text.find(end)
            if start < 0 or finish < 0:
                raise RecordError(
                    "%s carries no %s ... %s markers; this script will not "
                    "guess where the block belongs" % (page.name, begin, end))
            text = text[:start] + block + text[finish + len(end):]
        artifacts[page] = text
    return artifacts


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    persistence = load(PERSISTENCE)
    exceedance = load(EXCEEDANCE)
    conditional = load(EXCEEDANCE_GBM)
    artifacts = rendered(persistence, exceedance, conditional)

    if "--check" in argv:
        stale = []
        for path, text in sorted(artifacts.items()):
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current != text:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            sys.stderr.write(
                "stale, and the run records have moved under them: %s\n"
                "run: python3 scripts/emit_results.py\n" % ", ".join(stale))
            return 1
        print("README block and figures agree with docs/runs/.")
        return 0

    FIGURES.mkdir(parents=True, exist_ok=True)
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    for path, text in sorted(artifacts.items()):
        path.write_text(text, encoding="utf-8")
    print("wrote %s" % ", ".join(str(p.relative_to(ROOT)) for p in sorted(artifacts)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
