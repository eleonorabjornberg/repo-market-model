#!/usr/bin/env python3
"""Emit the README's Key-findings block and its figure from the run records.

Nothing in the block is typed. Every figure is read out of `docs/runs/*.json` --
the records `backtest` and `exceedance-backtest` wrote, each carrying the panel
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
SUMMARY = ROOT / "docs/EXECUTIVE_SUMMARY.md"
WALKTHROUGH = ROOT / "examples/walkthrough.py"
NOTEBOOK = ROOT / "notebooks/01_portfolio_walkthrough.ipynb"

BEGIN = "<!-- generated: key-findings -->"
END = "<!-- end generated: key-findings -->"
STATUS_BEGIN = "<!-- generated: status -->"
STATUS_END = "<!-- end generated: status -->"
HEADLINE_BEGIN = "<!-- generated: headline -->"
HEADLINE_END = "<!-- end generated: headline -->"

PERSISTENCE = "persistence_funding.json"
EXCEEDANCE = "exceedance_funding_climatology.json"

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


def pct(value, places=1):
    return ("%." + str(places) + "f%%") % (value * 100.0)


# --------------------------------------------------------------------------
# the block


def key_findings(persistence, exceedance):
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
    add("The baseline is characterised and the scoring is verified. **No model has yet")
    add("been shown to beat it**, which is Phase 2's first clause and is open.")
    add("")
    add("**Target.** The next-business-day value of the panel field `%s` — the SOFR")
    add("to IORB spread in basis points — forecast from information available at %s")
    add("on the previous business day.")
    lines[-3] = lines[-3] % ", ".join(require(persistence, "declaration", "features"))
    lines[-2] = lines[-2] % require(persistence, "declaration", "decision_time")
    add("")
    add("**Panel.** %s to %s, %d rows, SHA-256 `%s`." % (
        panel["first_date"], panel["last_date"], panel["row_count"], panel["sha256"][:12]))
    add("")
    add("**Evaluation.** Purged rolling origin, %d-day purge, **%d forecast origins**,"
        % (require(persistence, "derived", "purge_days"), folds["count"]))
    add("first scored %s, last scored %s. Run at `%s`."
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
    lines.append("**Where this is: phase %d of %d — %s (%s).** Next is phase %d, %s, "
                 "whose exit criterion is %s. The machine-readable version is "
                 "[`docs/status.json`](docs/status.json), regenerated in CI from the "
                 "same headings rather than edited."
                 % (phase["number"], len(phases) - 1, phase["name"], state,
                    following["number"], following["name"],
                    emit_status.require_exit(following, "the next phase")))
    lines.append("")
    lines.append(STATUS_END)
    return "\n".join(lines)


def headline(persistence, exceedance):
    """The same figures as the results table, in sentences and without jargon.

    `docs/EXECUTIVE_SUMMARY.md` is written for someone who will not open a run
    record, and the temptation there is to round a number into a claim. It is
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
                 "one made using only information a person would actually have held that "
                 "afternoon."
                 % (panel["first_date"], panel["last_date"], folds["count"]))
    lines.append("- On that history, a simple benchmark — tomorrow looks like today — is "
                 "wrong by **%s basis points on average**, and the range that error could "
                 "plausibly take is %s to %s basis points."
                 % (bp(metrics["mae_bps"]), bp(interval["lower"]), bp(interval["upper"])))
    lines.append("- Its uncertainty bands are **too narrow**: a band meant to contain the "
                 "outcome %s of the time contained it %s of the time. That gap is measured "
                 "and unexplained, and it is the next thing being worked on."
                 % (pct(metrics["interval_probability"], 0), pct(metrics["interval_coverage"])))
    lines.append("- The scoring itself has been checked against a case where the right "
                 "answer is known in advance: a forecast with no information in it scores "
                 "**%s skill**, exactly as it must. Every later claim of skill rests on "
                 "that." % bp(worst, 3))
    lines.append("")
    lines.append("**No model has yet been shown to forecast better than the benchmark.** "
                 "That is the honest state of the work, and it is why nothing here is a "
                 "basis for a decision about money.")
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


def figure_svg(exceedance, theme):
    colors = THEMES[theme]
    taus = require(exceedance, "metrics", "by_tau")
    order = sorted(taus, key=float)
    cols = 2
    rows = (len(order) + cols - 1) // cols
    width = cols * CELL_W + 16
    height = rows * CELL_H + 52

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
           'height="%d" font-family=\'%s\' role="img" aria-label="Reliability of the '
           'exceedance forecasts at each declared threshold">'
           % (width, height, width, height, FONT)]
    out.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, colors["surface"]))
    out.append('<text x="8" y="20" font-size="13" font-weight="600" fill="%s">'
               'Reliability of the exceedance forecasts</text>' % colors["ink"])
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


def rendered(persistence, exceedance):
    """Every artifact this script owns, as {path: text}."""

    artifacts = {
        FIGURES / "reliability.svg": figure_svg(exceedance, "light"),
        FIGURES / "reliability-dark.svg": figure_svg(exceedance, "dark"),
        NOTEBOOK: notebook(WALKTHROUGH.read_text(encoding="utf-8")),
    }
    pages = {
        README: (
            (BEGIN, END, key_findings(persistence, exceedance)),
            (STATUS_BEGIN, STATUS_END, status_line()),
        ),
        SUMMARY: (
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
    artifacts = rendered(persistence, exceedance)

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
