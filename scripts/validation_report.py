#!/usr/bin/env python3
"""The generated blocks of the model documentation and validation report (#119; rewritten for (s3c-ann-net), #1442).

`docs/model/validation.md` is written by hand in the model-risk structure Eleonora ruled on #119 (purpose and use,
data, methodology, assumptions and limitations, performance by regime, outcomes analysis, monitoring), then governance.
It documents one model, (s3c-ann-net), H5's frozen candidate (`docs/research/h5-candidate.json`;
`docs/research/hypotheses/H5.md`, step 6), and replaces the `gbm_funding` report of #841 and the phase 2 content: both
stay in git history and the records stay untouched in `docs/runs/`. Its known-limits block lists each limit Eleonora
accepted or kept visible (her rulings of 2 and 3 November 2026 on #1187 and #1316), each linked to the issue and the page
that show it; a page that does not exist raises `ReportError`.
**Its prose states no figure.** Every figure, date and count sits in a block this module renders, and
`scripts/emit_results.py` writes the blocks into the page between `<!-- generated: NAME -->` markers and refuses a stale
page with `--check`, exactly as it does for the README.

The blocks read one of four things, and nothing is typed here:

* a record in `docs/runs/` (the results, by way of the section functions of `emit_results.py`);
* a metadata or declaration file (`metadata/s3c_announced_settlement_1288.json`, the declaration of the measurement that
  scored the candidate; `metadata/spread_distribution_634.json`, the protocol's grid and benchmarks;
  `docs/research/h5-candidate.json`, the candidate's own record; `metadata/lockbox.json`, `metadata/sources.json`, `metadata/funding_panel_manifest.json`,
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
    """The declaration of the measurement that scored the candidate (#1288)."""

    return _json(ROOT / (candidate or _candidate())["declaration"])


def _protocol(candidate=None):
    """The declaration that carries the protocol's grid, horizons and benchmarks (#634)."""

    return _json(ROOT / (candidate or _candidate())["protocol_declaration"])


def _record(candidate=None):
    """`docs/research/h5-candidate.json`, the candidate's own record."""

    return _json(ROOT / (candidate or _candidate())["candidate_record"])


def _declared_candidate(candidate, declaration):
    for entry in declaration["candidates"]:
        if entry["name"] == candidate["declaration_candidate"]:
            return entry
    raise ReportError("the declaration %s has no candidate %r" % (candidate["declaration"],
                                                                   candidate["declaration_candidate"]))


def _bullets(items):
    return ["- %s" % item for item in items]


# --------------------------------------------------------------------------
# purpose and use


def use_limitation_block(emit):
    return ["**Use limitation.** " + _candidate()["use_limitation"], "",
            "(A proposal of the pull request that closes #1442, for Eleonora's review; `docs/use-limitation.md`, the "
            "phase 2 statement, is unchanged.)"]


def use_block(emit):
    """What the candidate forecasts, for whom, and what it must not be used for."""

    candidate = _candidate()
    declaration = _declaration(candidate)
    protocol = _protocol(candidate)
    horizons = protocol["horizons"]
    lines = [
        "**What it forecasts.** The candidate is %s, H5's frozen candidate. It forecasts the distribution of the spread of SOFR minus the administered reserve rate (IOER before 29 July 2021, IORB after; written SOFR − IORB) in "
        "basis points, as %d quantiles of the spread on each of the next %d to %d business days after the decision "
        "day. The primary score is %s (scoring protocol v1, `docs/decisions/scoring-protocol.md`)."
        % (candidate["label"], len(protocol["protocol"]["grid"]), horizons[0], horizons[-1],
           declaration["primary"]["metric"]),
        "",
        "**Hypothesis.** H5, the primary goal of the project (`docs/research/hypotheses/H5.md`): a registered "
        "distribution forecast of the spread beats as-of persistence and calendar climatology on this score by at "
        "least the minimum margin of the protocol, on prospective days. This report is H5's step 6, rewritten for the "
        "frozen candidate.",
        "",
        "**What it must not be used for.** It is not a stress-warning system and not a basis for VaR, limits, "
        "liquidity or capital, or desk sizing: \"warns of stress\" is never claimed. Its users are researchers and "
        "readers of the development pages; it carries no decision authority.",
    ]
    return lines


def candidate_block(emit):
    """The candidate as its own record and the declaration of the measurement that scored it state it."""

    candidate = _candidate()
    declaration = _declaration(candidate)
    protocol = _protocol(candidate)
    record = _record(candidate)
    entry = _declared_candidate(candidate, declaration)
    walk = declaration["frame"]["walk"].split(";")[0]
    from repo_model import decision_instant
    lines = [
        "**The model.** %s" % record["description"],
        "",
        "**What it is, as the declaration states it.** %s" % entry["definition"],
        "",
        "**The cap.** %s (%s; declared in `%s`)." % (record["cap"]["rule"][0].upper() + record["cap"]["rule"][1:],
                                                      record["cap"]["line"], record["cap"]["declaration"]),
        "",
        "**The sizing of the settlement terms.** %s (`%s`; declared in `%s`)." % (
            record["sizing"]["rule"][0].upper() + record["sizing"]["rule"][1:], record["sizing"]["module"],
            record["sizing"]["declaration"]),
        "",
        "**Inputs.** The target's own history and the calendar columns at the target day, on direct pairs "
        "(`training_pairs=\"direct\"`); the two settlement terms from the auction announcement, public from %s (%s); "
        "the SRF line and the standing_repo entry in force, as public at the decision instant. Nothing it reads is "
        "later than the decision instant (`docs/decisions/information-set.md`)."
        % (record["dating"]["instant"], record["dating"]["in_force"]),
        "",
        "**Levels and horizons.** The protocol's grid of %d levels, at horizons %s business days."
        % (len(protocol["protocol"]["grid"]), ", ".join(str(h) for h in protocol["horizons"])),
        "",
        "**Fitting.** A walk-forward fit; the declaration states the walk as \"%s\". The decision instant is %s %s. "
        "The development window is the decision days whose five targets are on or before %s; the 2026 days are shown "
        "apart and decide nothing."
        % (walk, decision_instant.DECISION_TIME_TEXT, decision_instant.DECISION_TIMEZONE,
           candidate["development_last_target_day"]),
        "",
        "**Status.** Not recalibrated: no recalibration layer corrects its quantiles. Frozen as the H5 candidate "
        "(%s, %s: %s) and not registered: no confirmation day has scored it." % (
            record["label"], record["date"], record["ruling"]),
        "",
        "**Declaration.** `%s`, declared by the pull request that closes #%s before any score was computed; the "
        "candidate's record is `%s`." % (candidate["declaration"], declaration["issue"], candidate["candidate_record"]),
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
        "tracked snapshots, so it rebuilds without a network (`REPRODUCIBILITY.md`). The decision time is the build "
        "setting of the instant forecasts are made at now (`repo_model.decision_instant`, the amendment of 29 October "
        "2026, #1312); the published records on this page were made at the earlier instant their own declarations "
        "state, and the panel's bytes and digest are the same at either."
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


def _lockbox_scope(first_tier, first_closed, development_last, last_day):
    if not development_last < first_tier:
        raise ReportError("the development window ends %s, which is not before the first tier %s"
                          % (development_last, first_tier))
    return ("**The development evidence in this report decides only on days to %s** (the development window of the "
            "declaration). The 2026 days up to %s are shown apart and decide nothing: they sit in the near-blind tier "
            "opened once on Eleonora's ruling and were seen by earlier studies. No day from %s is scored. The phase 2 "
            "records in `docs/runs/` scored other windows, each stated in its record; this report states none of their "
            "figures, and `docs/decisions/lockbox.md` records which of them are history and not a holdout."
            % (development_last, last_day, first_closed))


def lockbox_block(emit):
    declaration = _json(ROOT / "metadata/lockbox.json")
    candidate = _candidate()
    tiers = declaration["tiers"]
    first_closed = next((t["start"] for t in tiers if not t["opened"]), None)
    if first_closed is None:
        raise ReportError("every lockbox tier is open: the report's scope needs a closed tier to name")
    last_day = _declaration(candidate)["limits"]["last_day"]
    if not last_day < first_closed:
        raise ReportError("the candidate's evidence scores %s, which is not before the first closed day %s"
                          % (last_day, first_closed))
    lines = [
        "**The lockbox** (`docs/decisions/lockbox.md`, `metadata/lockbox.json`). A comparison scores only days in a "
        "tier that is open. %s" % _lockbox_scope(tiers[0]["start"], first_closed,
                                                 candidate["development_last_target_day"], last_day),
        "",
        "| Tier | Days | Opened |",
        "|---|---|---|",
    ]
    for tier in tiers:
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


def known_limits_block(emit):
    """Each known limit of the candidate, with its status and the issue and page that show it (#1442).

    Nothing is computed here and no figure is rendered: the pages carry the figures, as development data. A source
    names a page that exists or says why there is none yet; anything else raises `ReportError`.
    """

    candidate = _candidate()
    label = candidate["evidence_label"]
    lines = [
        "**Every limit below is %s** (scoring protocol v1, #640). Each is read on the studentized bound of mean d "
        "(her ruling on #1009) and is linked to the issue and the page that carry its figures; this report states "
        "none, and publishing one as a record is Eleonora's decision (`docs/decisions/publish-rule.md`). The limits "
        "of 2020, of the FOMC target days and of lead 1 are accepted as known limits by her rulings of 2 and 3 "
        "November 2026; the use limitation above stays." % label,
        "",
    ]
    for limit in candidate["known_limits"]:
        lines.append("- **%s.** %s" % (limit["title"], limit["limit"]))
        lines.append("  - *Status.* %s" % limit["status"])
        for source in limit["sources"]:
            if source.get("page"):
                if not (ROOT / source["page"]).exists():
                    raise ReportError("known limit %r cites %s, which does not exist" % (limit["id"], source["page"]))
                where = "`%s`" % source["page"]
            elif source.get("why_no_page"):
                where = "no page yet: %s" % source["why_no_page"]
            else:
                raise ReportError("known limit %r cites %s with neither a page nor a reason" % (limit["id"],
                                                                                                 source["issue"]))
            note = ": %s" % source["note"] if source.get("note") else ""
            lines.append("  - *Evidence.* %s, %s%s" % (source["issue"], where, note))
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
    protocol = _protocol(candidate)
    splits = _json(ROOT / "metadata/evaluation_splits.json")
    regimes = [r["label"] for r in splits["regimes"] if r["label"] != "2027"]
    day_types = [t.replace("_", "-") for t in splits["day_types"]["precedence"]]
    label = candidate["evidence_label"]
    lines = [
        "**Every result below is %s** (scoring protocol v1, #640). The candidate has no record in `docs/runs/`, so "
        "this report states no figure for it: each result is cited by its issue and its page, which carry the "
        "figures, and publishing one as a record is Eleonora's decision (`docs/decisions/publish-rule.md`)." % label,
        "",
        "**How it is scored** (the declaration `%s`, written before any score; the protocol's grid and benchmarks "
        "from `%s`)." % (candidate["declaration"], candidate["protocol_declaration"]),
        "",
        "- **Score.** %s; key secondary, %s; the Brier score of the pressure-day probability beside them."
        % (declaration["primary"]["metric"], declaration["primary"]["key_secondary"]),
        "- **Benchmarks.** B1, %s; B2, %s; B1' is the calendar-aware persistence of #960, reported beside B1. The "
        "baselines given the candidate's own cap are the confirmatory benchmarks (her ruling of 3 November 2026 on "
        "#1421), the uncapped versions beside them." % (protocol["benchmarks"]["B1"], protocol["benchmarks"]["B2"]),
        "- **Pairing.** Each day's difference is the benchmark's score minus the candidate's, so a positive value "
        "favours the candidate: %s." % protocol["protocol"]["difference"],
        "- **Interval.** %s." % declaration["scoring"]["test"].split(";")[0],
        "- **Reading.** %s." % declaration["scoring"]["reading"].split(". Lens")[0],
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
        "Read the known limits first (section 4): they are the splits where the candidate loses or its bands fail, "
        "and the pages above say how it stands in each. A pooled figure alone is not a result."])
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
    "validation-known-limits": known_limits_block,
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
