#!/usr/bin/env python3
"""The generated blocks of the plain-language results page (`site/plain.html`, #120).

The page says in plain words what the project forecasts, how well, against what, and where it fails, for a
reader with no finance background. **Its hand-written HTML states no figure.** Every figure, date and count sits
inside a block this module renders, and `scripts/emit_results.py` writes the blocks into the page between
`<!-- generated: NAME -->` markers and refuses a stale page with `--check`, as it does for the README, the final
test page and the validation report.

A block reads one of four things, and nothing is typed here:

* a record in `docs/runs/` (the results);
* a metadata or declaration file (`metadata/lockbox.json`, `metadata/stress_thresholds.json`,
  `metadata/funding_panel_manifest.json`, `docs/use-limitation.md`);
* the code's own declarations (`repo_model.scarcity`);
* `docs/model/external_sources.json`, which carries what is cited from outside the repository (the ruled claim
  wording, the fork note and the futures note).

Every section ends with its sources: a link to the record each claim rests on, and to the validation report
(`docs/model/validation.md`), which carries the full account. `tests/test_plain_page.py` refuses a section with no
record link, a link to a file that does not exist, and a digit typed outside a block.

Standard library only. `emit_results.py` calls `blocks`, passing itself.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

REPOSITORY = "eleonorabjornberg/repo-market-model"
BLOB = "https://github.com/%s/blob/main/" % REPOSITORY
VALIDATION = "docs/model/validation.md"
SOURCES = ROOT / "docs/model/external_sources.json"
USE_LIMITATION = ROOT / "docs/use-limitation.md"

#: The published pressure probability's records, one per horizon, and the one-day-ahead one the headline reads.
PRESSURE_RECORDS = "pressure_model_v1_h%d.json"
HEADLINE_HORIZON = 1
#: The distribution's pre-2026 comparison against as-of persistence, and the near-blind final test.
DISTRIBUTION_RECORD = "compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
FINAL_TEST_RECORD = "final_test_near_blind.json"
CLIMATOLOGY = "calendar guess"
PERSISTENCE = "“tomorrow looks like today” model"


class PageError(RuntimeError):
    """The page's inputs do not carry what a block needs. Do not guess."""


def _json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _e(text):
    return html.escape(str(text), quote=True)


def _link(path, label=None, *, run=False):
    """A link to a tracked file on `main`; a file that does not exist refuses to render."""

    rel = ("docs/runs/" + path) if run else path
    if not (ROOT / rel).exists():
        raise PageError("%s does not exist, so the page cannot link to it" % rel)
    return '<a href="%s%s">%s</a>' % (BLOB, _e(rel), _e(label or rel))


def _sources(emit, *records, extra=()):
    """The closing line of a section: its records, then the validation report."""

    links = [_link(name, name, run=True) for name in records]
    links.extend(extra)
    links.append(_link(VALIDATION, "the validation report"))
    return '<p class="src">Where this comes from: %s.</p>' % ", ".join(links)


def _table(headers, rows, caption):
    out = ['<div class="scroll"><table>', "<caption>%s</caption>" % _e(caption), "<thead><tr>"]
    out.extend("<th scope=\"col\">%s</th>" % _e(h) for h in headers)
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>%s</tr>" % "".join(
            ("<th scope=\"row\">%s</th>" if position == 0 else "<td>%s</td>") % _e(cell)
            for position, cell in enumerate(row)))
    out.append("</tbody></table></div>")
    return out


def _details(summary, lines):
    return ["<details>", "<summary>%s</summary>" % _e(summary)] + lines + ["</details>"]


def _clock(decision_time):
    hour, minute = int(decision_time[:2]), int(decision_time[3:5])
    return "%d%s %s" % (hour % 12 or 12, "" if minute == 0 else ":%02d" % minute, "am" if hour < 12 else "pm")


def _headline_taus(emit):
    thresholds = _json(ROOT / "metadata/stress_thresholds.json")
    taus = [int(tau) for tau in thresholds["taus_bp"] if str(int(tau)) in emit.HEADLINE_TAUS]
    if not taus:
        raise PageError("no headline threshold in metadata/stress_thresholds.json")
    return taus


def _paired(record, benchmark, tau):
    return emit_require(record, "benchmarks", benchmark, "by_tau", str(tau), "paired_brier_difference")


def emit_require(mapping, *path):
    value = mapping
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise PageError("record has no %s" % "/".join(path))
        value = value[key]
    return value


def _words(lower, upper):
    """What a paired interval supports, in plain words (a positive difference favours the model)."""

    if lower > 0:
        return "better"
    if upper < 0:
        return "worse"
    return "not clearly different"


def _level(entry):
    """The coverage level an interval states, as "90%", read off the record's own bootstrap."""

    return "%d%%" % round(100 * emit_require(entry, "level"))


def _range(entry, places):
    return "%+.*f to %+.*f" % (places, entry["lower"], places, entry["upper"])


# --------------------------------------------------------------------------
# the question


def question_block(emit):
    manifest = _json(ROOT / "metadata/funding_panel_manifest.json")
    taus = _headline_taus(emit)
    return [
        "<p>Banks, dealers and money funds lend each other cash overnight against U.S. Treasury securities. "
        "This is the repo market. The rate on that lending is called SOFR. The Federal Reserve also pays banks a "
        "rate on the money they keep with it, called IORB. Most days SOFR sits at or just below IORB. On some days "
        "spare cash runs short and SOFR jumps above it.</p>",
        "<p>This project forecasts the gap between the two, SOFR minus IORB, for the next business day. The "
        "headline forecast is the <strong>chance that the gap is more than %s basis points</strong>. A basis point "
        "is a hundredth of one percentage point. It uses public data only, and only what was public at %s on the "
        "day before the forecast. The public data runs from %s to %s.</p>"
        % (" and more than ".join("%d" % tau for tau in taus), _e(_clock(manifest["decision_time"])),
           _e(manifest["start_date"]), _e(manifest["end_date"])),
        '<p class="src">Where this comes from: %s, %s, and %s.</p>' % (
            _link("metadata/stress_thresholds.json"), _link("metadata/funding_panel_manifest.json"),
            _link(VALIDATION, "the validation report")),
    ]


# --------------------------------------------------------------------------
# how well: the pressure probability


def pressure_block(emit):
    """The headline: the chance of pressure, against its two benchmarks, then split by regime and day type."""

    taus = _headline_taus(emit)
    name = PRESSURE_RECORDS % HEADLINE_HORIZON
    record = emit.load(name)
    scored = emit_require(record, "metrics", "scored_days")
    last = emit_require(record, "folds", "last", "scored_date")
    lines = [
        "<p>Each day the model gives a probability that the gap will be above the line. A good probability forecast "
        "is neither too bold nor too timid. The usual measure is the Brier score: how far the forecast probability "
        "was from what happened, on average, where lower is better. Each result below is a <em>paired</em> "
        "difference: on every day, the benchmark's score minus the model's, averaged. A positive number means the "
        "model did better. The range after it is the %s interval, found by resampling the days.</p>"
        % _level(emit_require(record, "benchmarks", "persistence_logistic", "by_tau", str(taus[0]),
                              "paired_brier_difference", "interval")),
        "<p>Two benchmarks keep the model honest. The <strong>%s</strong> uses only how often pressure happens on "
        "each type of day (month-end, quarter-end, tax date, ordinary). The <strong>%s</strong> looks at today's "
        "gap and nothing else.</p>" % (_e(CLIMATOLOGY), _e(PERSISTENCE)),
    ]
    sentences = []
    cells = {}
    for tau in taus:
        entry = emit_require(record, "metrics", "by_tau", str(tau))
        parts = []
        for benchmark, label in (("calendar_climatology", CLIMATOLOGY), ("persistence_logistic", PERSISTENCE)):
            paired = _paired(record, benchmark, tau)
            interval = paired["interval"]
            cells[(tau, benchmark)] = (paired["mean"], interval)
            parts.append("against the %s the model was <strong>%s</strong> (%s, %s interval %s)" % (
                _e(label), _words(interval["lower"], interval["upper"]), "%+.4f" % paired["mean"],
                _level(interval), _range(interval, 4)))
        sentences.append(
            "<li><strong>More than +%d bp.</strong> This happened on %s of the %d days scored (every day up to "
            "%s). %s.</li>" % (tau, emit.pct(entry["base_rate"]), scored, _e(last),
                               "; ".join(parts)))
    lines.append("<ul class=\"results\">%s</ul>" % "".join(sentences))

    # Split by regime and by day type, against the persistence model, at the first threshold.
    first = taus[0]
    paired = _paired(record, "persistence_logistic", first)
    splits = emit_require(paired, "splits")
    tallies = {"better": 0, "worse": 0, "not clearly different": 0, "not enough days": 0}
    rows = []
    for group, title in (("by_regime", "Market period"), ("by_day_type", "Type of day")):
        for label, cell in emit_require(splits, group).items():
            if "interval" not in cell or "mean" not in cell:
                verdict = "not enough days"
                rows.append((title + ": " + label.replace("_", " "), str(cell.get("count", "")), "none", "", verdict))
            else:
                verdict = _words(cell["interval"]["lower"], cell["interval"]["upper"])
                rows.append((title + ": " + label.replace("_", " "), str(cell["count"]), "%+.4f" % cell["mean"],
                             _range(cell["interval"], 4), verdict))
            tallies[verdict] += 1
    total = sum(tallies.values())
    lines.append(
        "<p>The gain is not the same everywhere. Against the %s at +%d bp, the model was better in %d of %d "
        "groups of days, not clearly different in %d, worse in %d, and %d had too few days to say.</p>"
        % (_e(PERSISTENCE), first, tallies["better"], total, tallies["not clearly different"], tallies["worse"],
           tallies["not enough days"]))

    # The numbers: both thresholds, both benchmarks, all five horizons, and the splits.
    horizons = sorted(int(path.stem.rsplit("_h", 1)[1]) for path in emit.RUNS.glob("pressure_model_v1_h*.json"))
    rows_h = []
    for horizon in horizons:
        other = emit.load(PRESSURE_RECORDS % horizon)
        row = ["%d business day%s ahead" % (horizon, "" if horizon == 1 else "s")]
        for tau in taus:
            for benchmark, _ in (("calendar_climatology", 0), ("persistence_logistic", 0)):
                p = _paired(other, benchmark, tau)
                row.append("%+.4f (%s), %s" % (p["mean"], _range(p["interval"], 4),
                                               _words(p["interval"]["lower"], p["interval"]["upper"])))
        rows_h.append(tuple(row))
    headers = ["How far ahead"] + [
        "Above +%d bp, against the %s" % (tau, label) for tau in taus for label in (CLIMATOLOGY, PERSISTENCE)]
    lines.extend(_details("Show the numbers", (
        _table(headers, rows_h, "Brier-score gain over each benchmark, by how far ahead the forecast looks")
        + _table(["Group of days", "Days", "Gain", "Interval", "Verdict"], rows,
                 "Gain over the %s at +%d bp, by market period and type of day" % (PERSISTENCE, first)))))
    lines.append(_sources(emit, *(PRESSURE_RECORDS % horizon for horizon in horizons)))
    return lines


# --------------------------------------------------------------------------
# how well: the next-day range


def distribution_block(emit):
    """The next-day range forecast against as-of persistence: the earlier years, then the near-blind final test."""

    final = emit.load(FINAL_TEST_RECORD)
    cell = emit_require(final, "primary", "cell")
    earlier = emit.load(DISTRIBUTION_RECORD)
    comparison = emit_require(earlier, "comparison")
    interval = comparison["mean_difference_interval"]
    passed = emit_require(cell, "result") == "pass"
    lines = [
        "<p>The model also forecasts the whole range of where the gap could land, not just one number. This "
        "is the five-quantile score: it measures how far off the forecast range was, and lower is better. The "
        "benchmark is <strong>as-of persistence</strong>, which says tomorrow will look like the latest gap "
        "already public.</p>",
        "<ul class=\"results\">",
        "<li><strong>Earlier years.</strong> From %s to %s (%d forecasts) the model's score was %s bp and "
        "persistence's was %s bp. The gap is %s bp, %s interval %s bp, so the model was <strong>%s</strong>.</li>"
        % (_e(emit_require(earlier, "folds", "first", "scored_date")), _e(emit_require(earlier, "folds", "last",
                                                                                      "scored_date")),
           emit_require(comparison, "origin_count"), emit.bp(comparison["model_b"]["crps_bps"]),
           emit.bp(comparison["model_a"]["crps_bps"]), emit.signed(comparison["mean_difference_bps"], 2), _level(interval),
           "%s to %s" % (emit.signed(interval["lower"], 2), emit.signed(interval["upper"], 2)),
           _words(interval["lower"], interval["upper"])),
        "<li><strong>The final test, January to September 2026.</strong> %s</li>" % _e(_final_test_sentence(emit, cell,
                                                                                                         passed)),
        "</ul>",
        "<p>The final test was set up before it was run and run once, on days the model had not been tuned on by "
        "name. Those days had appeared inside earlier pooled results, so it is called <strong>near-blind</strong>, "
        "not blind. The first fully blind confirmation will come from the live daily record.</p>",
    ]
    rows = []
    for key, name in (("by_day_type", "Type of day"),):
        for label, group in emit_require(emit_require(cell, "splits"), key).items():
            if "interval" in group and "mean" in group:
                rows.append((name + ": " + label.replace("_", " "), str(group["count"]), emit.signed(group["mean"], 3),
                             "%s to %s" % (emit.signed(group["interval"]["lower"], 3),
                                           emit.signed(group["interval"]["upper"], 3))))
            else:
                rows.append((name + ": " + label.replace("_", " "), str(group.get("count", "")), "none", ""))
    lines.extend(_details("Show the numbers", _table(
        ["Group of days", "Days", "Gain, bp", "Interval, bp"], rows,
        "Final test: persistence's score minus the model's, by type of day (positive favours the model)")))
    lines.append(_sources(emit, DISTRIBUTION_RECORD, FINAL_TEST_RECORD,
                          extra=[_link("docs/final-test.md", "the final-test page")]))
    return lines


def _final_test_sentence(emit, cell, passed):
    figures = (emit.bp(emit_require(cell, "crps_published_bps"), 2), emit.bp(emit_require(cell, "crps_persistence_bps"), 2),
               emit._ft_interval(cell, 2))
    days = emit_require(cell, "days")
    level = _level(emit_require(cell, "interval"))
    if passed:
        return ("Over %d scored days the model's score was %s bp and persistence's was %s bp. The gap's %s interval, "
                "%s bp, lies above zero, so the model was better. A few days drive the mean, and 2026 was a calm "
                "year." % ((days,) + figures[:2] + (level,) + figures[2:]))
    return ("Over %d scored days the model's score was %s bp and persistence's was %s bp. The gap's %s interval, "
            "%s bp, includes zero, so the model was not shown to be better." % ((days,) + figures[:2] + (level,) + figures[2:]))


# --------------------------------------------------------------------------
# the scarcity state and the other desk outputs


def scarcity_block(emit):
    from repo_model import scarcity

    states = ", ".join("%s" % scarcity.STATE_LABELS[level] for level in sorted(scarcity.STATE_LABELS))
    low, high = scarcity.SATIATION_BAND
    lines = [
        "<p>Pressure is more likely when bank reserves, the cash banks keep at the Fed, are scarce. The model "
        "therefore shows a <strong>scarcity state</strong> beside each forecast: one of %s. It is a label "
        "for what is happening now. It is not an input to the forecast, and it is not itself a forecast.</p>"
        % _e(states),
        "<p>The label is set by two cut-points. Reserves count as ample or tight depending on where they stand "
        "as a share of all commercial-bank assets: %s%% to %s%% is the band where banks stop treating reserves as "
        "abundant. And the Fed's overnight reverse repo facility is a buffer only while it holds more than "
        "$%d billion; below that it no longer absorbs a drain on reserves. Both cut-points were chosen from the "
        "literature and from the same history they are checked on, so they describe the market and have not been "
        "proven in a separate test.</p>" % (
            "%g" % (low * 100), "%g" % (high * 100), int(scarcity.ON_RRP_BUFFER_BN)),
        "<p>Besides the pressure probability and the scarcity state, the model's daily outputs are the range of "
        "the gap on scheduled pressure days one to five days ahead, and the expected contribution of a "
        "month-end or quarter-end turn to the period average. They report on the same frozen model. "
        "They are described in the validation report and have no separate scored record yet.</p>",
        _sources(emit, extra=[_link("src/repo_model/scarcity.py"), _link("scripts/desk_outputs.py")]),
    ]
    return lines


# --------------------------------------------------------------------------
# where it falls short


def _plain_use_limitation():
    text = USE_LIMITATION.read_text(encoding="utf-8")
    start = text.index("\n## Plain-English version\n")
    end = text.find("\n## ", start + 1)
    found = [line[2:].strip() for line in text[start:end if end >= 0 else None].splitlines() if line.startswith("> ")]
    if len(found) != 1 or not found[0]:
        raise PageError("docs/use-limitation.md must carry exactly one plain-English blockquote; found %d" % len(found))
    return found[0]


def limits_block(emit):
    declaration = _json(ROOT / "metadata/lockbox.json")
    first_locked = declaration["tiers"][0]["start"]
    last_scored = emit.require(emit.load(emit.PERSISTENCE), "folds", "last", "scored_date")
    final = emit.load(FINAL_TEST_RECORD)
    taus = _headline_taus(emit)
    events = {}
    for document in emit_require(final, "events_reported_only"):
        if "targets" in document and document.get("horizon") == 1:
            for tau in taus:
                events[tau] = emit_require(document, "targets", "+%dbp" % tau, "all_days")
            break
    if len(events) != len(taus):
        raise PageError("the final test record carries no event counts for the headline thresholds")
    record = emit.load(PRESSURE_RECORDS % HEADLINE_HORIZON)
    top = taus[-1]
    paired = _paired(record, "persistence_logistic", top)["interval"]
    climatology = _paired(record, "calendar_climatology", top)["interval"]
    scale = emit_require(emit_require(final, "primary", "cell"), "days")
    lines = [
        "<p class=\"limit\">%s</p>" % _e(_plain_use_limitation()),
        "<ul class=\"results\">",
        "<li><strong>Few severe days.</strong> Of the %d days of the final test, %s were above +%d bp and %s above "
        "+%d bp. Such days are rare, so the evidence about them is thin.</li>" % (
            scale, events[taus[0]]["events"], taus[0], events[top]["events"], top),
        "<li><strong>The test above +%d bp is weak.</strong> On the earlier years the model's gain over the %s at "
        "+%d bp has a %s interval of %s, so it was <strong>%s</strong>. Against the %s it was <strong>%s</strong>.</li>" % (
            top, _e(PERSISTENCE), top, _level(paired), _range(paired, 4), _words(paired["lower"], paired["upper"]),
            _e(CLIMATOLOGY), _words(climatology["lower"], climatology["upper"])),
        "<li><strong>Days that are locked.</strong> %s</li>" % _lockbox_sentence(first_locked, last_scored),
        "</ul>",
    ]
    lines.extend(_details("The statement of record", ["<p>%s</p>" % _e(emit.use_limitation())]))
    lines.append(_sources(emit, PRESSURE_RECORDS % HEADLINE_HORIZON, FINAL_TEST_RECORD,
                          extra=[_link("docs/use-limitation.md"), _link("metadata/lockbox.json"),
                                 _link("docs/decisions/lockbox.md", "the lockbox rule")]))
    return lines


def _lockbox_sentence(first_locked, last_scored):
    return _e("Some days are kept sealed so that no result can be tuned on them. A comparison scores only days "
              "before %s. The older pooled distribution tables scored days through %s (the near-blind period); "
              "the results published since score only days before %s." % (first_locked, last_scored, first_locked))


# --------------------------------------------------------------------------
# where the project sits


def place_block(emit):
    data = _json(SOURCES)
    claim = data["claim"]["sentence"]
    links = []
    for source in data["sources"]:
        links.append('<li><a href="%s">%s</a></li>' % (_e(source["url"]), _e(source["label"])))
    fork = data["fork"]["text"].replace("`", "")
    futures = data["futures"]["text"]
    return [
        "<p>%s</p>" % _e(claim),
        "<ul class=\"results\">%s</ul>" % "".join(links),
        "<p>%s</p>" % _e(fork),
        "<p>%s</p>" % _e(futures),
        '<p class="src">Where this comes from: %s, and %s.</p>' % (
            _link("docs/model/external_sources.json"), _link(VALIDATION, "the validation report")),
    ]


BLOCKS = {
    "plain-question": question_block,
    "plain-pressure": pressure_block,
    "plain-distribution": distribution_block,
    "plain-scarcity": scarcity_block,
    "plain-limits": limits_block,
    "plain-place": place_block,
}


def blocks(emit):
    """`[(begin, end, text)]` for `emit_results.rendered`, one entry per block of the page."""

    found = []
    for name, build in BLOCKS.items():
        body = "\n".join(build(emit))
        begin = "<!-- generated: %s -->" % name
        end = "<!-- end generated: %s -->" % name
        found.append((begin, end, "\n".join([
            begin, "<!-- Generated by scripts/emit_results.py (scripts/plain_page.py) from docs/runs/, metadata/ and "
            "docs/. Do not edit by hand. -->", body, end])))
    return found


if __name__ == "__main__":
    raise SystemExit("run scripts/emit_results.py: it writes these blocks into site/plain.html")
