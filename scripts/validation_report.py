#!/usr/bin/env python3
"""The generated blocks of the model documentation and validation report (#119; rewritten for H5's candidate, #841).

`docs/model/validation.md` is written by hand in the model-risk structure Eleonora ruled on #119 (purpose and use,
data, methodology, assumptions and limitations, performance by regime, outcomes analysis, monitoring), then governance.
It documents one model, `gbm_funding`, H5's candidate (`docs/research/hypotheses/H5.md`, step 6), and replaces the
phase 2 content: the phase 2 version stays in git history and its records stay untouched in `docs/runs/`.
**Its prose states no figure.** Every figure, date and count sits in a block this module renders, and
`scripts/emit_results.py` writes the blocks into the page between `<!-- generated: NAME -->` markers and refuses a stale
page with `--check`, exactly as it does for the README.

The blocks read one of four things, and nothing is typed here:

* a record in `docs/runs/` (the results, by way of the section functions of `emit_results.py`);
* a metadata or declaration file (`metadata/spread_distribution_634.json`, the declaration of the measurement that
  scored the candidate; `metadata/lockbox.json`, `metadata/sources.json`, `metadata/funding_panel_manifest.json`,
  `metadata/evaluation_splits.json`, the decision records);
* the code's own declarations (`scripts/live_score.py`);
* `docs/model/candidate.json`, `docs/model/external_sources.json` and `docs/model/controls.json`, which carry the
  candidate's use limitation, assumptions, limitations and development evidence, what is cited from outside the
  repository (the ruled claim wording, the clearing mandate, the sources and whether a session fetched each one) and
  the guards the controls section lists.

The candidate has no record in `docs/runs/`: every result about it is development data, cited by its issue and its
page and labelled "development data, not a verdict" (scoring protocol v1). Publishing a figure as a record is
Eleonora's decision (`docs/decisions/publish-rule.md`), so no performance figure is rendered here. A control is listed
only while its guard and its test file exist and the test records a mutation (`RecordError` otherwise), so the list
cannot outlive the test.

Standard library only. `emit_results.py` calls `blocks`, passing itself.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

MODEL = ROOT / "docs/model"
SOURCES = MODEL / "external_sources.json"
CONTROLS = MODEL / "controls.json"
DECISIONS = ROOT / "docs/decisions"

CANDIDATE = MODEL / "candidate.json"

#: The decision records the governance section lists in this order, then any record not named.
GOVERNANCE_FIRST = ("workflow.md", "publish-rule.md", "information-set.md", "lockbox.md", "pressure-probability.md",
                    "final-test-preregistration.md", "live-scoring-declaration.md")


class ReportError(RuntimeError):
    """The report's inputs do not carry what a block needs. Do not guess."""


def _json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _candidate():
    return _json(CANDIDATE)


def _declaration(candidate=None):
    return _json(ROOT / (candidate or _candidate())["declaration"])


def _bullets(items):
    return ["- %s" % item for item in items]


# --------------------------------------------------------------------------
# purpose and use


def use_limitation_block(emit):
    return ["**Use limitation.** " + _candidate()["use_limitation"], "",
            "(A proposal of the pull request that closes #841, for Eleonora's review; `docs/use-limitation.md`, the "
            "phase 2 statement, is unchanged.)"]


def use_block(emit):
    """What the candidate forecasts, for whom, and what it must not be used for."""

    candidate = _candidate()
    declaration = _declaration(candidate)
    horizons = declaration["horizons"]
    lines = [
        "**What it forecasts.** The candidate is `%s`. It forecasts the distribution of the SOFR − IORB spread in "
        "basis points, as %d quantiles of the spread on each of the next %d to %d business days after the decision "
        "day. The primary score is %s (scoring protocol v1, `docs/decisions/scoring-protocol.md`)."
        % (candidate["candidate"], len(declaration["protocol"]["grid"]), horizons[0], horizons[-1],
           declaration["metrics"]["primary"]),
        "",
        "**Hypothesis.** H5, the primary goal of the project (`docs/research/hypotheses/H5.md`): a registered "
        "distribution forecast of the spread beats as-of persistence and calendar climatology on this score by at "
        "least the minimum margin of the protocol, on prospective days. This report is H5's step 6.",
        "",
        "**What it must not be used for.** It is not a stress-warning system and not a basis for VaR, limits, "
        "liquidity or capital, or desk sizing: \"warns of stress\" is never claimed. Its users are researchers and "
        "readers of the development pages; it carries no decision authority.",
    ]
    return lines


def candidate_block(emit):
    """The candidate as the declaration of the measurement that scored it states it."""

    candidate = _candidate()
    declaration = _declaration(candidate)
    control = declaration["controls"][candidate["declaration_control"]]
    base = declaration["inputs"]["base"]
    scoring = declaration["scoring"]
    lines = [
        "**The model.** `%s`: %s" % (candidate["candidate"], control),
        "",
        "**Inputs.** %s: %s. %s" % ("The published funding declaration's features",
                                    ", ".join("`%s`" % c for c in base["columns"]), base["reading"] + "."),
        "",
        "**Levels and horizons.** The protocol's grid of %d levels, at horizons %s business days, read at each "
        "lead by the as-of rule (`asof.InformationRule(horizon=h)`)."
        % (len(declaration["protocol"]["grid"]), ", ".join(str(h) for h in declaration["horizons"])),
        "",
        "**Fitting.** A walk-forward fit, minimum history %d scored days, refitted every %d scored days, "
        "decision time %s. A decision day is scored when every one of its target days is on or before %s and has a "
        "published outcome." % (scoring["minimum_history"], scoring["refit_every"], scoring["decision_time"],
                                scoring["last_target_day"]),
        "",
        "**Status.** Uncalibrated: no recalibration layer corrects its quantiles. Not registered: it is a "
        "candidate of the development steps of H5 and no confirmation day has scored it.",
        "",
        "**Declaration.** `%s`, declared by the pull request that closes #%s before any score was computed."
        % (candidate["declaration"], declaration["issue"]),
    ]
    return lines


# --------------------------------------------------------------------------
# conceptual soundness: the literature and where the project stands


def literature_block(emit):
    data = _json(SOURCES)
    claim = data["claim"]
    lines = [claim["sentence"], "", "(" + claim["ruling"] + ".)", "", "The sources:", ""]
    for source in data["sources"]:
        lines.append("- %s: %s (%s)" % (source["label"], source["url"], _fetched(source, data)))
    lines.extend(["", data["fork"]["text"], "", data["futures"]["text"]])
    return lines


def _fetched(source, data):
    if source["fetched"]:
        return "fetched %s" % data["fetched_on"]
    return "not fetched: this environment's network policy refused the host, so the citation is as ruled"


# --------------------------------------------------------------------------
# data


def data_block(emit):
    manifest = _json(ROOT / "metadata/funding_panel_manifest.json")
    registry = _json(ROOT / "metadata/sources.json")
    lines = [
        "**The published panel.** %s to %s, %d rows, SHA-256 `%s`, decision time %s, built at the cutoff %s from "
        "tracked snapshots, so it rebuilds without a network (`REPRODUCIBILITY.md`)."
        % (manifest["start_date"], manifest["end_date"], manifest["row_count"], manifest["sha256"][:12],
           manifest["decision_time"], manifest["build_cutoff"]),
        "",
        "**The registry, `metadata/sources.json`.** Each input is read at the latest value public at its decision "
        "instant, per field (`docs/decisions/information-set.md`). The availability rule is the registry's "
        "`release_lag`; a field with its own lag is listed with it. The registry also declares scheduled "
        "availability for the inputs known in advance (the calendar, the FOMC schedule, Treasury settlements, "
        "announced IORB changes).",
        "",
        "| Source | Provider | Frequency | Availability (lag, time, basis) | Fields with their own lag |",
        "|---|---|---|---|---|",
    ]
    for name, entry in registry.items():
        lag = entry.get("release_lag", {})
        own = entry.get("field_release_lags", {})
        lines.append("| `%s` | %s | %s | %s | %s |" % (
            name, entry.get("provider", ""), entry.get("frequency", ""), _lag(lag),
            ", ".join("%s (%s)" % (f, _lag(v)) for f, v in sorted(own.items())) or "none"))
    return lines


def _lag(lag):
    if not lag:
        return "not declared"
    if "days" not in lag:
        return lag.get("basis", "not declared").replace("_", " ")
    unit = lag.get("unit", "days").replace("_", " ")
    if lag["days"] == 1:
        unit = unit.rstrip("s")
    return "%s %s, %s, %s" % (lag["days"], unit, lag.get("available_time", "n/a"),
                             lag.get("basis", "n/a").replace("_", " "))


def _lockbox_scope(first_locked, last_target):
    if not last_target < first_locked:
        raise ReportError("the development evidence scores %s, which is not before the first locked day %s"
                          % (last_target, first_locked))
    return ("**The development evidence in this report scores only days before %s** (the last target day of the "
            "measurement's declaration is %s). The phase 2 records in `docs/runs/` scored other windows, each "
            "stated in its record; this report states none of their figures, and `docs/decisions/lockbox.md` "
            "records which of them are history and not a holdout." % (first_locked, last_target))


def lockbox_block(emit):
    declaration = _json(ROOT / "metadata/lockbox.json")
    first_locked = declaration["tiers"][0]["start"]
    last_target = _declaration()["scoring"]["last_target_day"]
    lines = [
        "**The lockbox** (`docs/decisions/lockbox.md`, `metadata/lockbox.json`). A comparison scores only days "
        "before the first locked day. %s" % _lockbox_scope(first_locked, last_target),
        "",
        "| Tier | Days | Opened |",
        "|---|---|---|",
    ]
    for tier in declaration["tiers"]:
        span = "%s to %s" % (tier["start"], tier["end"]) if tier["end"] else "from %s, every day after the tier "\
            "before" % tier["start"]
        opened = ("opened %s, once, on Eleonora's ruling (%s)" % (tier["opened"]["date"], tier["opened"]["ruling"])
                  if tier["opened"] else "not opened: no record has scored these days")
        lines.append("| %s | %s | %s |" % (tier["name"].replace("_", "-"), span, opened))
    lines.extend([
        "",
        "Every scoring entry point refuses a scored day in a tier that is not opened, with `LookAheadError`. An "
        "opened tier becomes ordinary history, and the near-blind tier's single pre-registered opening is reported "
        "separately and labelled."])
    return lines


# --------------------------------------------------------------------------
# implementation and controls


def controls_block(emit):
    controls = _json(CONTROLS)["controls"]
    lines = ["| Kind | What it guards | Guard | Test | Mutation recorded |", "|---|---|---|---|---|"]
    for control in controls:
        test = ROOT / control["test"]
        guard = ROOT / control["guard"]
        if not test.exists() or not guard.exists():
            raise ReportError("control %r names a missing file" % control["what"])
        if not re.search(r"(?i)recorded mutation|mutation record", test.read_text(encoding="utf-8")):
            raise ReportError("%s records no mutation, so it cannot be listed as a control" % control["test"])
        lines.append("| %s | %s | `%s` | `%s` | yes |" % (control["kind"], control["what"], control["guard"],
                                                         control["test"]))
    lines.extend([
        "",
        "A new leakage, availability or staleness guard is added with one recorded mutation that kills it, in the "
        "test's docstring (`CLAUDE.md`). CI (`.github/workflows/tests.yml`) runs the whole suite as one process and "
        "refuses a stale generated page; a leakage guard raises `LookAheadError`, never `assert`, and a data guard "
        "raises `ValueError`. The suite has zero `expectedFailure`."])
    return lines


# --------------------------------------------------------------------------
# assumptions and limitations


def assumptions_block(emit):
    return _bullets(_candidate()["assumptions"])


def limitations_block(emit):
    candidate = _candidate()
    lines = _bullets(candidate["limitations"])
    lines.extend(["", "**Open questions, for Eleonora.** This report settles none of them:", ""])
    lines.extend(_bullets(candidate["open_questions"]))
    return lines


# --------------------------------------------------------------------------
# performance by regime, and outcomes


def performance_block(emit):
    """How the candidate is scored, and where each development result is, cited by issue and page.

    The candidate has no record in `docs/runs/`, so no figure is rendered: each row names the issue and the page
    that carry it. The splits are those of `metadata/evaluation_splits.json`.
    """

    candidate = _candidate()
    declaration = _declaration(candidate)
    splits = _json(ROOT / "metadata/evaluation_splits.json")
    regimes = [r["label"] for r in splits["regimes"] if r["label"] != "2027"]
    day_types = [t.replace("_", "-") for t in splits["day_types"]["precedence"]]
    label = candidate["evidence_label"]
    lines = [
        "**Every result below is %s** (scoring protocol v1, #640). The candidate has no record in `docs/runs/`, so "
        "this report states no figure for it: each result is cited by its issue and its page, which carry the "
        "figures, and publishing one as a record is Eleonora's decision (`docs/decisions/publish-rule.md`)." % label,
        "",
        "**How it is scored** (the declaration `%s`, written before any score)." % candidate["declaration"],
        "",
        "- **Score.** %s; key secondary, %s." % (declaration["metrics"]["primary"], declaration["metrics"]["key_secondary"]),
        "- **Benchmarks.** B1, %s; B2, %s." % (declaration["benchmarks"]["B1"], declaration["benchmarks"]["B2"]),
        "- **Pairing.** Each day's difference is the benchmark's score minus the candidate's, so a positive value "
        "favours the candidate: %s." % declaration["protocol"]["difference"],
        "- **Interval.** %s." % declaration["protocol"]["interval"],
        "- **Regimes** (of the decision day, drawn after the fact): %s." % ", ".join(regimes),
        "- **Pressure-day types** (of the target day): %s." % ", ".join(day_types),
        "",
        "| Result | Issue | Page | Script | Splits it reports | Status |",
        "|---|---|---|---|---|---|",
    ]
    for row in candidate["evidence"]:
        for key in ("page", "script"):
            if not (ROOT / row[key]).exists():
                raise ReportError("%s does not exist" % row[key])
        lines.append("| %s | %s | `%s` | `%s` | %s | %s |" % (
            row["what"], row["issue"], row["page"], row["script"], row["split"], label))
    lines.extend([
        "",
        "Read the regimes after 2020 and the quarter-end and tax-date types first: the phase 2 models were weakest "
        "there, and the pages above say how the candidate stands in each. A pooled figure alone is not a result."])
    return lines


def outcomes_block(emit):
    """Outcomes analysis: there is none yet, and what it will be."""

    candidate = _candidate()
    return [
        "**There is no outcome to analyse yet.** The candidate is not registered and no prospective confirmation "
        "day has scored it. An outcomes analysis compares forecasts with what happened on days the forecasts did not "
        "see; under scoring protocol v1 only prospective days give a verdict (#640), and development days never do.",
        "",
        "**What the analysis will be.** %s" % candidate["monitoring"]["checkpoints"],
        "",
        "**Until then.** The development results are in the table above, labelled %s. They set the baseline that "
        "the first checkpoint is read against, and they decide nothing." % candidate["evidence_label"],
    ]


def clearing_block(emit):
    data = _json(SOURCES)
    c = data["clearing"]
    dates = " and of ".join("%s **%s**" % (d["what"], d["when"]) for d in c["dates"])
    note = lambda item: "" if item["fetched"] else "; not fetched: this environment's network policy refused the host"
    lines = [
        "**The Treasury clearing mandate.** (%s.)" % c["scope"],
        "",
        "- **The dates.** The SEC's Treasury clearing rule requires central clearing of %s (%s: %s%s). %s %s "
        "(%s) says it requires %s." % (
            dates, c["release"], c["release_url"], note({"fetched": c["release_fetched"]}),
            "The release itself was not read, so the timing rests on the scope; the New York Fed's speech,",
            c["speech"]["label"], c["speech"]["url"], c["speech"]["says"]),
        "- **What it means for the target.** %s (%s, %s). Repo migrating into clearing therefore drifts SOFR's "
        "composition and volume. The migration is gradual and already under way: %s." % (
            c["methodology"]["says"][0].upper() + c["methodology"]["says"][1:], c["methodology"]["label"],
            c["methodology"]["url"], c["speech"]["cleared_share"]),
        "- **The expected effect.** The expectation of little change to SOFR's median but fatter tails is the "
        "OFR's (%s: %s%s). This project's target is the tail." % (
            c["ofr_blog"]["label"], c["ofr_blog"]["url"], note(c["ofr_blog"])),
        "  %s" % c["dates_note"],
        "- **Where it falls.** Both compliance dates fall after the panel ends (%s), so there is no clean break "
        "inside the scoring window or the near-blind tier. The drift overlaps the 2025 regime and the locked "
        "period: watch it when the lockbox is opened, above all for any input built on `SOFR_volume`."
        % c["panel_end"],
    ]
    return lines


# --------------------------------------------------------------------------
# monitoring


def monitoring_block(emit):
    import importlib.util

    spec = importlib.util.spec_from_file_location("live_score_for_validation", ROOT / "scripts/live_score.py")
    live = importlib.util.module_from_spec(spec)
    sys.modules["live_score_for_validation"] = live
    spec.loader.exec_module(live)

    monitoring = _candidate()["monitoring"]
    declaration = (DECISIONS / "live-scoring-declaration.md")
    if not declaration.exists():
        raise ReportError("docs/decisions/live-scoring-declaration.md is missing")
    return [
        "**The live record.** %s" % monitoring["live_record"],
        "",
        "**What the live record does today, for the published model** (#215, #254). From %s, every business day "
        "after the decision instant, `.github/workflows/live-log.yml` logs the published model's forecast, frozen, "
        "at a pinned code commit, before any outcome exists; the log is verified against its published digests "
        "before any score is read (`scripts/live_integrity.py`); a missed day is recorded as missed, not "
        "back-filled; and the scorer refuses to run on any date other than the pre-registered ones "
        "(`scripts/live_score.py`)." % live.FIRST_LIVE_DAY.isoformat(),
        "",
        "**Checkpoints.** %s" % monitoring["checkpoints"],
        "",
        "**Revalidation.** %s" % monitoring["revalidation"],
    ]


# --------------------------------------------------------------------------
# governance


def governance_block(emit):
    records = []
    for path in sorted(DECISIONS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M)
        status = re.search(r"\*\*Status[^*]*\*\*", text)
        words = " ".join(status.group(0).strip("*").split()) if status else "no status line"
        records.append((path.name, title.group(1) if title else path.stem, words.split(". ")[0].rstrip(".") + "."))
    order = {name: i for i, name in enumerate(GOVERNANCE_FIRST)}
    records.sort(key=lambda r: (order.get(r[0], len(order)), r[0]))
    lines = ["| Decision record | Title | Status line |", "|---|---|---|"]
    for name, title, status in records:
        lines.append("| `docs/decisions/%s` | %s | %s |" % (name, title, status.replace("|", "/")))
    lines.extend([
        "",
        "The records in `docs/decisions/drafts/` are drafts for Eleonora and are in force only once she merges "
        "them. Her ruling on #112 delegates the review and merge of queued pull requests to the \"Directive "
        "loop\" routine until she revokes it in writing (`docs/decisions/workflow.md`, \"Delegated review\")."])
    return lines


# --------------------------------------------------------------------------

#: `{block name: function(emit) -> list of lines}`, in the order of the page.
BLOCKS = {
    "validation-use-limitation": use_limitation_block,
    "validation-use": use_block,
    "validation-data": data_block,
    "validation-lockbox": lockbox_block,
    "validation-candidate": candidate_block,
    "validation-literature": literature_block,
    "validation-controls": controls_block,
    "validation-assumptions": assumptions_block,
    "validation-limitations": limitations_block,
    "validation-clearing": clearing_block,
    "validation-performance": performance_block,
    "validation-outcomes": outcomes_block,
    "validation-monitoring": monitoring_block,
    "validation-governance": governance_block,
}


def blocks(emit):
    """`[(begin, end, text)]` for `emit_results.rendered`, one entry per block of the page."""

    found = []
    for name, build in BLOCKS.items():
        body = "\n".join(build(emit))
        begin = "<!-- generated: %s -->" % name
        end = "<!-- end generated: %s -->" % name
        found.append((begin, end, "\n".join([
            begin, "<!-- Generated by scripts/emit_results.py (scripts/validation_report.py) from docs/runs/, "
            "metadata/ and docs/model/. Do not edit by hand. -->", "", body, "", end])))
    return found
