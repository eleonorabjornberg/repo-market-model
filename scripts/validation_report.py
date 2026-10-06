#!/usr/bin/env python3
"""The generated blocks of the model documentation and validation report (#119).

`docs/model/validation.md` is written by hand in the model-risk structure Eleonora ruled on
4 October 2026 (purpose and use, conceptual soundness, data, implementation and controls,
performance and outcomes, limitations, monitoring, governance). **Its prose states no figure.**
Every figure, date and count sits in a block this module renders, and `scripts/emit_results.py`
writes the blocks into the page between `<!-- generated: NAME -->` markers and refuses a stale
page with `--check`, exactly as it does for the README and `docs/final-test.md`.

The blocks read one of four things, and nothing is typed here:

* a record in `docs/runs/` (the results, by way of the section functions of `emit_results.py`);
* a metadata or declaration file (`metadata/lockbox.json`, `metadata/sources.json`,
  `metadata/funding_panel_manifest.json`, `metadata/stress_thresholds.json`, the decision records);
* the code's own declarations (`repo_model.onset`, `scripts/live_score.py`);
* `docs/model/external_sources.json` and `docs/model/controls.json`, which carry what is cited from
  outside the repository (the ruled claim wording, the clearing mandate, the sources and whether a
  session fetched each one) and the guards the controls section lists.

A result that is only a scratch measurement, with no record in `docs/runs/`, is cited by its issue and
carries no number (`SCRATCH`). A control is listed only while its guard and its test file exist and the
test records a mutation (`RecordError` otherwise), so the list cannot outlive the test.

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

#: Results that are scratch measurements: a script ran, no record in `docs/runs/` was written, and the
#: figure is not stated here. Each is cited by its issue (Eleonora's directive: "say so and cite the issue
#: instead of a number"). Every script must exist, or the block refuses to render.
SCRATCH = (
    ("The four desk outputs: the pressure probability, the scheduled-pressure-day quantiles at each horizon, "
     "the turn's expected contribution and the scarcity regime state", "#232", "scripts/desk_outputs.py",
     "reporting only, on the frozen model; the live record's file schema does not change"),
    ("The reserve-scarcity indicator, validated on pressure-day frequency", "#115",
     "scripts/scarcity_validation.py",
     "published as a displayed state only, with its declared cut-points; it is not a model input (Eleonora's ruling "
     "on #157), so no result here depends on it"),
    ("The onset post-mortem: every onset before 2026, its calendar, scarcity state and both forecasts", "#214",
     "scripts/onset_post_mortem.py", "descriptive only; it decides nothing and claims nothing"),
    ("Pressure model v1.1: the new inputs, switched on for the run only", "#117", "scripts/pressure_v1_1.py",
     "every input stays off in every published declaration"),
    ("The knowledge holdout and the H.4.1 lag", "#280", "scripts/knowledge_holdout_lag_study.py",
     "two reported-only studies; the live model keeps its declared H.4.1 lag"),
    ("Scoring every candidate on the small-leap and leap-onset targets, then CRPS, then the stress thresholds",
     "#139", "scripts/recalibration_bakeoff.py",
     "the final test's leap cells are published (above); the wider candidate scoring is a scratch measurement and "
     "its leap result is a different question from a stress warning, never presented as one"),
)

#: The decision records the governance section lists in this order, then any record not named.
GOVERNANCE_FIRST = ("workflow.md", "publish-rule.md", "information-set.md", "lockbox.md", "pressure-probability.md",
                    "final-test-preregistration.md", "live-scoring-declaration.md")


class ReportError(RuntimeError):
    """The report's inputs do not carry what a block needs. Do not guess."""


def _json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _strip(block, *, headings=True):
    """A section function's text without its own markers, comment, headings and duplicated use limitation."""

    out = []
    skipping = False
    for line in block.split("\n"):
        if line.startswith("<!-- ") and line.endswith("-->"):
            continue
        if headings and line.startswith("## "):
            continue
        if line.startswith("**Use limitation.**"):
            skipping = True
            continue
        if skipping:
            if line.strip():
                skipping = False
            else:
                continue
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


# --------------------------------------------------------------------------
# purpose and use


def use_limitation_block(emit):
    return ["**Use limitation.** " + emit.use_limitation()]


def use_block(emit):
    """What the model forecasts, for whom, the four desk outputs and what it must not be used for."""

    from repo_model import onset

    thresholds = _json(ROOT / "metadata/stress_thresholds.json")
    taus = [tau for tau in thresholds["taus_bp"] if str(int(tau)) in emit.HEADLINE_TAUS]
    horizons = sorted(int(p.stem.rsplit("_h", 1)[1]) for p in emit.RUNS.glob("pressure_model_v1_h*.json"))
    if not taus or not horizons:
        raise ReportError("no headline threshold or pressure-model horizon found")
    jumps = ", ".join("h = %d: %s bp" % (h, emit.bp(onset.LEAP_JUMP_BP[h], 2)) for h in sorted(onset.LEAP_JUMP_BP))
    lines = [
        "**What it forecasts.** The target is `%s`. The headline is the **pressure probability**: the probability "
        "that the spread is strictly above %s, in whole basis points, at horizons of %d to %d business days "
        "(`docs/decisions/pressure-probability.md`)."
        % (thresholds["target"], " and ".join("+%d bp" % tau for tau in taus), horizons[0], horizons[-1]),
        "",
        "**The four desk outputs** (Eleonora's scope of 5 October 2026 on #119, from #232), which are the model's "
        "intended use and what monitoring watches:",
        "",
        "1. the pressure probability (headline);",
        "2. spread quantiles on scheduled pressure days, at each horizon;",
        "3. the turn's expected contribution to the period average;",
        "4. the scarcity regime state.",
        "",
        "**An additional target, small leaps and leap onsets.** A jump measured against each forecast's as-of "
        "anchor, with one threshold per horizon (%s; the exact percentile rule is `repo_model.onset`'s, at the "
        "%d%% percentile). A leap claim must beat both named baselines, calendar climatology and the "
        "persistence-logistic refitted to the leap target. A leap result is a different question from a stress "
        "warning and is never presented as one."
        % (jumps, int(round(onset.LEAP_PERCENTILE * 100))),
        "",
        "**What it must not be used for.** It is not a stress-warning system and not a basis for VaR, limits, "
        "liquidity or capital, or desk sizing: \"warns of stress\" is never claimed. Its users are researchers and "
        "readers of the published records; it carries no decision authority.",
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


def _lockbox_scope(first_locked, last_scored):
    if last_scored < first_locked:
        return "**Every record scores only days before %s.**" % first_locked
    return ("**The older pooled distribution tables scored days through %s (the near-blind tier); the records "
            "published since score only days before %s.** Each table states the window it scores. "
            "`docs/decisions/lockbox.md` records this, and the older figures are history, not a holdout."
            % (last_scored, first_locked))


def lockbox_block(emit):
    declaration = _json(ROOT / "metadata/lockbox.json")
    first_locked = declaration["tiers"][0]["start"]
    persistence = emit.load(emit.PERSISTENCE)
    last_scored = emit.require(persistence, "folds", "last", "scored_date")
    lines = [
        "**The lockbox** (`docs/decisions/lockbox.md`, `metadata/lockbox.json`). A comparison scores only days "
        "before the first locked day. %s" % _lockbox_scope(first_locked, last_scored),
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
# performance and outcomes


def distribution_block(emit):
    """The next-day distribution against as-of persistence, then each challenger, by regime and day type."""

    persistence = emit.load(emit.PERSISTENCE)
    require = emit.require
    metrics = require(persistence, "metrics")
    folds = require(persistence, "folds")
    interval = require(metrics, "mae_bps_interval")
    coverage = require(metrics, "interval_calibration", "coverage_interval")
    lines = [
        "**The benchmark, as-of persistence.** Over %d scored origins (%s to %s, refitted every %d scored days), "
        "its mean absolute error is %s bp (90%% interval %s to %s bp) and its CRPS is %s bp. A nominal %s%% "
        "interval covered %s of the realised outcomes (interval %s to %s)."
        % (folds["count"], folds["first"]["scored_date"], folds["last"]["scored_date"],
           require(persistence, "declaration", "refit_every"), emit.bp(require(metrics, "mae_bps")),
           emit.bp(interval["lower"]), emit.bp(interval["upper"]), emit.bp(require(metrics, "crps_bps")),
           emit.bp(require(metrics, "interval_probability") * 100, 0),
           emit.pct(require(metrics, "interval_coverage")),
           emit.pct(coverage["lower"]), emit.pct(coverage["upper"])),
        "",
    ]
    table, groups = emit.challenger_section()
    lines.extend(table)
    lines.append("")
    lines.append("**The paired difference by regime and by pressure-day type** (persistence's CRPS minus the "
                 "challenger's, bp, with its 90% interval):")
    lines.append("")
    for position, challengers in enumerate(groups):
        if position:
            lines.extend([emit.window_heading(challengers[0][1]), ""])
        split_rows = [(label, emit.require(record, "comparison", "splits")) for label, record in challengers]
        lines.extend(emit.split_matrix(split_rows, "by_regime"))
        lines.append("")
        lines.extend(emit.split_matrix(split_rows, "by_day_type"))
        lines.append("")
    lines.append("**Interval coverage on the same origins.**")
    lines.append("")
    for position, challengers in enumerate(groups):
        if position:
            lines.extend([emit.window_heading(challengers[0][1]), ""])
        lines.extend(emit.coverage_section(challengers, persistence))
        lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def pressure_block(emit):
    lines = list(emit.pressure_section())
    v1 = emit.pressure_v1_section()
    if v1:
        lines.extend([""] + list(v1))
    return lines


def final_test_block(emit):
    return _strip(emit.final_test_section())


def calibration_block(emit):
    """The calibration method as the records state it, and where the published band does not hold."""

    lines = []
    seen = []
    for name in emit.CORRECTION_WORDING:
        for text in emit.load(name).get("limitations", ()):
            if text.startswith(emit.RULED_WORDING) and text not in seen:
                seen.append(text)
    if not seen:
        raise ReportError("no record carries the ruled calibration wording")
    declaration = emit.require(emit.load(emit.CORRECTION_WORDING[0]), "declaration")
    lines.append("**The method, as declared in the published record.** The calibration is `%s`, on features %s."
                 % (declaration.get("calibration", "not declared"),
                    ", ".join("`%s`" % f for f in declaration.get("features", ()))))
    lines.append("")
    lines.append("The ruled wording, quoted from the records that carry it:")
    lines.append("")
    for text in seen:
        lines.append("- %s" % text[len(emit.RULED_WORDING):])
    lines.extend(["", emit.band_coverage_module().finding_sentence(emit.band_coverage()[1]), "",
                  "The split is `docs/band_coverage_by_split.md`, generated by the same script from the same records."])
    return lines


def lag_block(emit):
    """The lag finding as a validation result: the purge-rule records against the as-of records they became.

    Each pair is an archived record (`docs/runs/archive/pre-asof/`, unedited) and the record that replaced it.
    The figures are read off both records; the origins differ (the as-of rule scores from an earlier day), so each
    row states both counts.
    """

    pairs = (("persistence_funding.json", "persistence_funding.json"), ("backtest_gbm_mh61.json", "backtest_gbm.json"))
    lines = [
        "**The finding** (`docs/pivot/lag-assessment.md`): the earlier design read every input at a feature row "
        "chosen by a calendar-day purge, so the published \"next-business-day\" forecasts used inputs about a "
        "week old. Every record was re-scored under the as-of rule (`docs/decisions/information-set.md`) and the "
        "earlier ones were archived unedited. The assessment's own figures are scouting figures; the table is the "
        "records'.",
        "",
        "| Model | Rule | Scored origins | First feature date → scored date | Mean absolute error, bp | CRPS, bp |",
        "|---|---|---|---|---|---|",
    ]
    archive = ROOT / "docs/runs/archive/pre-asof"
    for old_name, new_name in pairs:
        for rule, record in (("purge (archived)", _json(archive / old_name)), ("as-of", emit.load(new_name))):
            folds = emit.require(record, "folds")
            metrics = emit.require(record, "metrics")
            first = folds["first"]
            lines.append("| `%s` | %s | %d | %s → %s | %s | %s |" % (
                new_name, rule, folds["count"], first["feature_date"], first["scored_date"],
                emit.bp(emit.require(metrics, "mae_bps"), 3), emit.bp(emit.require(metrics, "crps_bps"), 3)))
    purge = emit.require(_json(archive / "persistence_funding.json"), "derived", "purge_days")
    lines.extend(["", "The archived records name the rule they were scored under: a purge of %d calendar days "
                  "(`derived.purge_days`)." % purge])
    return lines


def desk_block(emit):
    """The results that are scratch measurements: cited by issue, no number."""

    lines = ["These are measurements, not records in `docs/runs/`, so this page states no figure from them. Each "
             "is cited by its issue, and its script is tracked.", "",
             "| Result | Issue | Script | Status |", "|---|---|---|---|"]
    for what, issue, script, status in SCRATCH:
        if not (ROOT / script).exists():
            raise ReportError("%s does not exist" % script)
        lines.append("| %s | %s | `%s` | %s |" % (what, issue, script, status))
    return lines


# --------------------------------------------------------------------------
# limitations


def limitations_block(emit):
    lines = list(emit.limitations_section())
    text = emit.USE_LIMITATION.read_text(encoding="utf-8")
    start = text.index("\n## The reasons\n")
    end = text.find("\n## ", start + 1)
    reasons = _join_bullets(text[start:end if end >= 0 else None])
    if not reasons:
        raise ReportError("docs/use-limitation.md lists no reasons")
    lines.extend(["", "**The reasons for the use limitation** (`docs/use-limitation.md`, each from a finding of the "
                  "independent review):", ""] + reasons)
    lines.extend(["", "**The near-blind tier is not a clean holdout.** The records state it: %s." % emit.FINAL_TEST_HEDGE])
    return lines


def _join_bullets(section):
    """The bullets of a section, each continued line joined to its bullet."""

    bullets = []
    for line in section.splitlines():
        if line.startswith("- "):
            bullets.append(line)
        elif line.startswith("  ") and bullets:
            bullets[-1] += " " + line.strip()
    return bullets


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
    from repo_model import onset

    first, second = live.FIRST_SCORING_DATES
    declaration = (DECISIONS / "live-scoring-declaration.md")
    if not declaration.exists():
        raise ReportError("docs/decisions/live-scoring-declaration.md is missing")
    lines = [
        "**The live record is this section** (#215, #222, #225, #254). From %s, every business day after the "
        "decision instant, `.github/workflows/live-log.yml` logs the published model's forecast, frozen, at a "
        "pinned code commit, with the day's baselines at each horizon, before any outcome exists."
        % live.FIRST_LIVE_DAY.isoformat(),
        "",
        "- **Daily frozen forecasts.** One JSON file per decision day on the `live-log` branch (`scripts/live_record.py`); "
        "a missed day is recorded as missed, not back-filled (`live_record.py missed`).",
        "- **Digests and failure tracking.** The log is verified against its published digests before any score is "
        "read (`scripts/live_integrity.py`), and a run that failed is reported rather than silently skipped.",
        "- **Interim reports.** Scored only on the pre-registered dates, the first two of which both fall in %d "
        "(`live_score.FIRST_SCORING_DATES`), then every 1 October, cumulatively from the first logged day; on "
        "any other date the scorer refuses to run (`scripts/live_score.py`)." % first.year,
        "- **The primary result.** The %s of the published distribution against as-of persistence's, at horizon %d, "
        "with the final test's pass rule, labels and block-10 sensitivity interval."
        % (live.HEADLINE["target"].upper(), live.HEADLINE["horizon"]),
        "- **The event-based leap verdict** (#222): reported only where a cell has at least %d events "
        "(`onset.MINIMUM_EVENTS`), as the leap result against both baselines; below that the cell is "
        "labelled `%s`. The pooled-event count at which the verdict is made is #222's and the final test "
        "pre-registration's, and is not restated here." % (onset.MINIMUM_EVENTS, live.TOO_FEW_DAYS),
        "- **The blind gap** (#235): %s." % live.GAP_LABEL,
        "",
        "**What monitoring covers.** The four desk outputs: the pressure probability (headline), the spread "
        "quantiles on scheduled pressure days at each horizon, the turn's expected contribution to the period "
        "average, and the scarcity regime state. The revalidation triggers, proposed and not decided, are in "
        "`docs/use-limitation.md`.",
    ]
    return lines


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
        "reviewer\" routine until she revokes it in writing (`docs/decisions/workflow.md`, \"Delegated review\")."])
    return lines


# --------------------------------------------------------------------------

#: `{block name: function(emit) -> list of lines}`, in the order of the page.
BLOCKS = {
    "validation-use-limitation": use_limitation_block,
    "validation-use": use_block,
    "validation-literature": literature_block,
    "validation-data": data_block,
    "validation-lockbox": lockbox_block,
    "validation-controls": controls_block,
    "validation-distribution": distribution_block,
    "validation-pressure": pressure_block,
    "validation-final-test": final_test_block,
    "validation-calibration": calibration_block,
    "validation-lag": lag_block,
    "validation-desk": desk_block,
    "validation-limitations": limitations_block,
    "validation-clearing": clearing_block,
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
