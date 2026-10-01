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
PRESSURE_BEGIN = "<!-- generated: pressure -->"
PRESSURE_END = "<!-- end generated: pressure -->"

PERSISTENCE = "persistence_funding.json"
EXCEEDANCE = "exceedance_funding_climatology.json"
EXCEEDANCE_GBM = "exceedance_gbm_mh61.json"

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


def sentence(text):
    """`text` with its first letter capitalised, to open a sentence."""

    return text[:1].upper() + text[1:]


def pct(value, places=1):
    return ("%." + str(places) + "f%%") % (value * 100.0)


# --------------------------------------------------------------------------
# the block


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

    levels = sorted(pinball, key=float)
    skills = sorted(taus, key=float)
    worst_skill = max(abs(taus[key]["brier_skill_score"]) for key in skills)

    lines = []
    add = lines.append
    add(BEGIN)
    add("<!-- Generated by scripts/emit_results.py from docs/runs/. Do not edit by hand:")
    add("     the block is regenerated from the run records and checked in the suite. -->")
    add("")
    # The tail sentence is read off the conditional record rather than typed: if a
    # re-run ever carries skill into the tail, this paragraph stops saying it does not.
    add("Every figure here is scored under the as-of information rule "
        "([`docs/decisions/information-set.md`](docs/decisions/information-set.md)). "
        "The records scored under the earlier rule, which read every input about a week "
        "stale, are archived in [`docs/runs/archive/pre-asof/`](docs/runs/archive/pre-asof/). "
        "Phase 2's verdicts were stated on those records, and none is restated here: "
        "whether each still holds is Eleonora's to rule.")
    add("")
    add("**Target.** The next-business-day value of the panel field `%s` — the SOFR "
        "to IORB spread in basis points — with the forecast made at %s on the previous "
        "business day. Each input is read at its latest value public at that instant; "
        "the calendar and scheduled Treasury settlements are read at the scored day."
        % (", ".join(require(persistence, "declaration", "features")),
           require(persistence, "declaration", "decision_time")))
    add("")
    add("**Panel.** %s to %s, %d rows, SHA-256 `%s`." % (
        panel["first_date"], panel["last_date"], panel["row_count"], panel["sha256"][:12]))
    add("")
    add("**Evaluation.** One as-of fold grid, expanding window, refitted every %d scored "
        "days, **%d forecast origins**, first scored %s, last scored %s. Run at `%s`."
        % (require(persistence, "declaration", "refit_every"), folds["count"],
           folds["first"]["scored_date"], folds["last"]["scored_date"], commit))
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
    # The verdict is computed from the record, not written: if a re-run ever
    # brackets the nominal probability, the paragraph says so instead.
    excludes = not (coverage["lower"] <= nominal <= coverage["upper"])
    add("**The coverage line is the honest one, and it is %s.** A nominal %s "
        "interval covered %s of %d realised outcomes. Intervalled the same way as the "
        "error above (stationary bootstrap, block length %d, %d replications, seed %d), "
        "the realised coverage lies between %s and %s, which %s the nominal "
        "probability. %s"
        % ("a finding" if excludes else "not yet a finding",
           pct(metrics["interval_probability"], 0),
           pct(metrics["interval_coverage"]), folds["count"],
           coverage["block_length"], coverage["replications"], coverage["seed"],
           pct(coverage["lower"]), pct(coverage["upper"]),
           "excludes" if excludes else "includes",
           "What the gap is — a miscalibrated benchmark, or one a challenger will "
           "improve on — is open, and no verdict is asserted in the suite."
           if excludes else
           "The gap is within what resampling the same history produces."))
    add("")
    lines.extend(backtest_splits(persistence))
    add("")
    table, challengers = challenger_section()
    lines.extend(table)
    add("")
    add("**Interval coverage on the same origins.**")
    add("")
    lines.extend(coverage_section(challengers))
    add("")
    add("**The control that licenses every future skill number.** A climatology scored "
        "against climatology must show no skill. Over the same %d origins its Brier "
        "skill score is %s at every declared threshold (%s bp), and its reference Brier "
        "score equals its own at each one. Any skill this repository later reports rests "
        "on that having been true first."
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
        "the as-of rule, refitted every %d scored days, against a climatology refitted on "
        "the same training rows. Run at `%s`." % (scored, refit, commit))
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
    add("The skill interval excludes zero "
        "above climatology at %s, and below it at %s. The last column is resolution as a "
        "share of uncertainty -- how much of the discrimination a sample had available "
        "the forecasts actually realised. It is the honest form of the comparison, "
        "because resolution and uncertainty both collapse as the event gets rarer and "
        "a resolution quoted alone cannot tell a model that stopped discriminating "
        "from a sample with nothing left to discriminate. It is %s at %g bp and "
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
    add("The same CORP reliability curves for the conditional model. Compare them with "
        "the climatology control above: a panel that hugs the diagonal at a low "
        "threshold and collapses onto a single forecast value at a high one is the "
        "table's resolution column, drawn.")
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

    Every row of a generated table must share the origins, panel, refit cadence and
    history it was scored on, or the table ranks numbers that are not
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
                 "taus_bp", "twcrps_weights", "benchmarks")


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
                          "refit cadence and origin count: %s" % sorted(keys))

    labels = labelled([require(r, "declaration", "model_b") for r in found])
    return sorted(zip(labels, found),
                  key=lambda pair: -pair[1]["comparison"]["mean_difference_bps"])


def labelled(declarations):
    """A label per declared model: its name and settings, then its own features.

    Two declarations whose settings agree are told apart by the features they
    alone use -- the ARX pair differ only in their exogenous columns, the
    funding and settlement exceedance records in their money columns. Two that
    agree on those too are refused.
    """

    labels = [_settings(declaration) for declaration in declarations]
    for label in set(labels):
        group = [i for i, value in enumerate(labels) if value == label]
        if len(group) < 2:
            continue
        sets = [set(require(declarations[i], "features")) for i in group]
        shared = set.intersection(*sets)
        for i, features in zip(group, sets):
            own = sorted(features - shared)
            if not own:
                raise RecordError("two records declare the same model, settings and "
                                  "features: %s" % label)
            labels[i] = "%s with %s" % (label, ", ".join("`%s`" % f for f in own))
    return labels


def challenger_section():
    rows = challenger_records()
    first = rows[0][1]
    comparison = first["comparison"]
    lines = []
    add = lines.append
    add("**Challengers against persistence.** Each challenger is scored on the same "
        "%d origins (minimum history %d, refit every %d); persistence's CRPS is %s bp. "
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
    add("")
    lines.extend(challenger_splits(rows))
    return lines, rows


SPLITS = (("by_regime", "regime"), ("by_day_type", "pressure-day type"))


def _cell(value, interval, places=2):
    """`+0.12 (−0.05, +0.30)`: a paired difference and its interval, or the value alone."""

    if interval is None:
        return ("%+." + str(places) + "f") % value
    return ("%+." + str(places) + "f (%+." + str(places) + "f, %+." + str(places) + "f)") % (
        value, interval["lower"], interval["upper"])


def backtest_splits(persistence):
    """Persistence's figures per regime and per pressure-day type."""

    metrics = require(persistence, "metrics")
    lines = []
    add = lines.append
    for split, name in SPLITS:
        entries = require(metrics, split)
        add("**Persistence by %s.** %s." % (name, sentence(require(metrics, "splits", split))))
        add("")
        add("| %s | Origins | MAE | CRPS | Interval coverage |" % name.capitalize())
        add("|---|---|---|---|---|")
        for label in entries:
            entry = entries[label]
            add("| %s | %d | %s bp | %s bp | %s |" % (
                label, entry["forecast_count"], bp(entry["mae_bps"]),
                bp(entry["crps_bps"]), pct(entry["interval_coverage"])))
        add("")
    return lines[:-1]


def challenger_splits(rows):
    """Each challenger's paired CRPS difference per regime and per pressure-day type."""

    lines = []
    add = lines.append
    comparisons = [record["comparison"] for _label, record in rows]
    for split, name in SPLITS:
        labels = list(require(comparisons[0], split))
        for c in comparisons:
            if list(require(c, split)) != labels:
                raise RecordError("challengers split %s over different strata" % split)
        add("<details><summary>Challengers against persistence by %s: CRPS difference, "
            "bp, with its 90%% interval</summary>" % name)
        add("")
        add("%s. Each stratum's origins are resampled in scored order with the run's "
            "block length; a positive value favours the challenger."
            % sentence(require(comparisons[0], "splits", split)))
        add("")
        add("| Challenger | %s |" % " | ".join(
            "%s (%d)" % (label, comparisons[0][split][label]["origin_count"])
            for label in labels))
        add("|---|%s" % ("---|" * len(labels)))
        for (label, record), c in zip(rows, comparisons):
            add("| %s | %s |" % (label, " | ".join(
                _cell(c[split][stratum]["mean_difference_bps"],
                      c[split][stratum].get("mean_difference_interval"))
                for stratum in labels)))
        add("")
        add("</details>")
        add("")
    return lines[:-1]


# --------------------------------------------------------------------------
# the pressure probability against its benchmarks

EXCEEDANCES = "exceedance_*.json"
BENCHMARKS = ("calendar-climatology", "persistence-logistic")
#: The headline thresholds, `docs/decisions/pressure-probability.md`.
HEADLINE_TAUS = (5.0, 10.0)


def exceedance_records():
    """Every exceedance record, labelled, scored on one grid and paired with both benchmarks."""

    found = []
    for path in sorted(RUNS.glob(EXCEEDANCES)):
        with path.open(encoding="utf-8") as handle:
            found.append(json.load(handle))
    if not found:
        raise RecordError("no %s record in docs/runs/" % EXCEEDANCES)
    grids = set((require(r, "panel", "sha256"), require(r, "declaration", "refit_every"),
                 require(r, "folds", "first", "scored_date"),
                 require(r, "folds", "last", "scored_date")) for r in found
                if require(r, "declaration", "minimum_history") == 61)
    if len(grids) != 1:
        raise RecordError("exceedance records at minimum history 61 are not on one grid: %s"
                          % sorted(grids))
    found = [r for r in found if require(r, "declaration", "minimum_history") == 61]
    for record in found:
        model = require(record, "declaration", "model")
        declared = set(require(record, "declaration", "benchmarks"))
        if declared != set(BENCHMARKS) - {model}:
            raise RecordError("%s is paired with %s, not with both benchmarks"
                              % (model, sorted(declared)))
    labels = labelled([require(r, "declaration") for r in found])
    return list(zip(labels, found))


def pressure_section():
    rows = exceedance_records()
    first = rows[0][1]
    commit = require(first, "provenance", "code", "commit")[:7]
    lines = []
    add = lines.append
    add(PRESSURE_BEGIN)
    add("<!-- Generated by scripts/emit_results.py from docs/runs/. Do not edit by hand:")
    add("     the block is regenerated from the run records and checked in the suite. -->")
    add("")
    add("Every exceedance record on the %d-origin grid (minimum history 61, refit every "
        "%d), each paired day by day with the two benchmarks of "
        "[`docs/decisions/pressure-probability.md`](docs/decisions/pressure-probability.md): "
        "**calendar-type climatology**, the training frequency of the event on days of the "
        "scored day's pressure-day type, and **persistence-logistic**, a logistic model of "
        "the event on the latest spread public at the decision. The difference is the "
        "benchmark's Brier score minus the model's, so a positive value favours the model; "
        "its 90%% interval is a stationary bootstrap on the per-day differences. Which "
        "candidate is the pressure probability is not chosen here: that choice is put to "
        "Eleonora. Run at `%s`."
        % (require(first, "metrics", "scored_days"), require(first, "declaration", "refit_every"),
           commit))
    add("")
    for tau in HEADLINE_TAUS:
        key = "%g" % tau
        entry = require(first, "metrics", "by_tau", key)
        add("**P(spread > %g bp)**, the event on %d of %d scored days (%s)."
            % (tau, entry["positives"], entry["scored_days"], pct(entry["base_rate"])))
        add("")
        add("| Model | Brier | Average precision | vs calendar climatology | "
            "vs persistence-logistic |")
        add("|---|---|---|---|---|")
        for label, record in rows:
            row = require(record, "metrics", "by_tau", key)
            cells = []
            for name in BENCHMARKS:
                if name == record["declaration"]["model"]:
                    cells.append("(itself)")
                    continue
                bench = require(row, "benchmarks", name)
                cells.append(_cell(bench["mean_brier_difference"],
                                   bench.get("mean_brier_difference_interval"), 4))
            add("| %s | %.4f | %s | %s | %s |" % (
                label, row["brier"],
                "%.3f" % row["average_precision"] if "average_precision" in row else "n/a",
                cells[0], cells[1]))
        add("")
        for split, name in SPLITS:
            strata = list(require(first, "metrics", "by_tau", key, split))
            add("<details><summary>P(spread > %g bp) by %s: Brier difference against "
                "persistence-logistic, with its 90%% interval</summary>" % (tau, name))
            add("")
            add("%s. Positives in each stratum: %s."
                % (sentence(require(first, "metrics", "splits", split)),
                   ", ".join("%s %d of %d" % (s, first["metrics"]["by_tau"][key][split][s]["positives"],
                                             first["metrics"]["by_tau"][key][split][s]["scored_days"])
                             for s in strata)))
            add("")
            add("| Model | %s |" % " | ".join(strata))
            add("|---|%s" % ("---|" * len(strata)))
            for label, record in rows:
                row = require(record, "metrics", "by_tau", key, split)
                if list(row) != strata:
                    raise RecordError("%s splits %s over different strata" % (label, split))
                cells = []
                for stratum in strata:
                    if record["declaration"]["model"] == "persistence-logistic":
                        cells.append("(itself)")
                        continue
                    bench = require(row, stratum, "benchmarks", "persistence-logistic")
                    cells.append(_cell(bench["mean_brier_difference"],
                                       bench.get("mean_brier_difference_interval"), 4))
                add("| %s | %s |" % (label, " | ".join(cells)))
            add("")
            add("</details>")
            add("")
    add("The calendar-climatology comparisons per stratum, and the 20 and 50 bp "
        "thresholds, are in each record under `metrics.by_tau`.")
    add("")
    add(PRESSURE_END)
    return "\n".join(lines)


def coverage_section(challengers):
    """Interval coverage of every backtest scored on the challengers' origins."""

    reference = _Scored.key(challengers[0][1])
    found = []
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
    for record in sorted(found, key=lambda r: r["declaration"]["model"]):
        metrics = require(record, "metrics")
        calibration = require(metrics, "interval_calibration")
        interval = require(calibration, "coverage_interval")
        nominal = require(calibration, "declared_probability")
        pinball = require(metrics, "pinball_loss")
        level = [key for key in pinball if float(key) == top][0]
        model = _settings(require(record, "declaration"))
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
    folds = require(persistence, "folds")
    panel = require(persistence, "panel")
    taus = require(exceedance, "metrics", "by_tau")
    worst = max(abs(taus[key]["brier_skill_score"]) for key in taus)

    lines = [HEADLINE_BEGIN]
    lines.append("<!-- Generated by scripts/emit_results.py from docs/runs/. -->")
    lines.append("")
    lines.append("- The forecasting machinery has been run end to end on real market data "
                 "covering %s to %s, and scored at **%d separate decision points** — each "
                 "one made only from the latest information public at 4 pm the day before."
                 % (panel["first_date"], panel["last_date"], folds["count"]))
    lines.append("- On that history, a simple benchmark — the latest spread public at the "
                 "decision, carried forward — is "
                 "wrong by **%s basis points on average**, and the range that error could "
                 "plausibly take is %s to %s basis points."
                 % (bp(metrics["mae_bps"]), bp(interval["lower"]), bp(interval["upper"])))
    lines.append("- Its uncertainty bands %s: a band meant to contain the "
                 "outcome %s of the time contained it %s of the time."
                 % ("are **too narrow**" if metrics["interval_coverage"]
                    < metrics["interval_probability"] else "are not too narrow",
                    pct(metrics["interval_probability"], 0), pct(metrics["interval_coverage"])))
    lines.append("- The scoring itself has been checked against a case where the right "
                 "answer is known in advance: a forecast with no information in it scores "
                 "**%s skill**, exactly as it must. Every later claim of skill rests on "
                 "that." % bp(worst, 3))
    beating = [label for label, record in challenger_records()
               if record["comparison"]["mean_difference_interval"]["lower"] > 0]
    lines.append("- %d of %d challenger models score better than the benchmark over the "
                 "same decision points, with an interval that excludes no difference."
                 % (len(beating), len(challenger_records())))
    lines.append("")
    lines.append("**Every result is also broken down by period and by type of day below, "
                 "and the pressure probability is compared with two benchmarks.** Which "
                 "model becomes the published pressure probability is a decision still to "
                 "be made, and nothing here is a basis for a decision about money.")
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
            (PRESSURE_BEGIN, PRESSURE_END, pressure_section()),
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
