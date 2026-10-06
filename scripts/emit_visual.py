#!/usr/bin/env python3
"""Emit the visual layer: docs/visual/data/*.json and site/index.html (directive 06, #118).

The results page: the plumbing, eight years of the spread, why pressure
happens, and what is known at the decision time (directive 06's descriptive
half); the forecast against its benchmarks and how it is graded (#118's model
half); and how the project was built. Nothing on the page is typed:

* The panel is rebuilt from the tracked fixtures with the repository's own
  `build` command and refused unless its SHA-256 is the published manifest's.
* Every event label and claim about market structure comes from
  `docs/visual/annotations.json`, each with a primary source. `metadata/` is
  read and never written.
* The administered rates in chapter 1 are parsed from a checksummed copy of the
  current FOMC implementation note, never transcribed.
* A placeholder left unfilled is an error, and so is a run record that does
  not declare the as-of information rule (`require_as_of`).
* Every model figure is read from a published run record in `docs/runs/`
  through `from_record`, which refuses a figure no record carries. A model
  figure that no published record carries yet (lead time) is a generated
  placeholder, and the generator refuses that placeholder once a
  record carries the figure (`pending_figures`).
* The "Final test" section (#238) reads `docs/runs/final_test_near_blind.json`
  alone, through `from_record`: the verdict, the pre-registered claim (quoted
  only on a pass, beside the near-blind disclosure), the split by day type and
  the reported-only cells with their verbatim labels.
* Days in a locked tier of `metadata/lockbox.json` (`docs/decisions/lockbox.md`)
  are drawn greyed and labelled "held out", and are left out of every count,
  share, median and generated sentence (#141 ruling 3). The tiers are read
  through `repo_model.lockbox`; a tier marked opened is ordinary history.
* The "Start here" block above the chapters is the newcomer layer (#141). Its
  terms come from `docs/visual/glossary.json`, each with a primary source; its
  views hold out the same locked days, through the same reader.
* View N3 reads the New York Fed's ON RRP results from the tracked snapshots in
  `tests/fixtures/snapshots/on_rrp_inputs/` through the repository's own
  adapter, which checks each file against its manifest's SHA-256 (#141 answer
  6). The panel and its digest do not change; the data file lists each
  snapshot's SHA-256.
* The reserve-scarcity state (#115) is shaded behind N1's line and drawn as a
  band lane in N3 (#148), under Eleonora's ruling of 2 October 2026 on #148:
  display only, no model reads it. It is read as-of on the published scored
  grid by `scarcity.pressure_days_by_state`, the function #115's validation
  used, from the measurement panel `scripts/scarcity_validation.py` builds
  from tracked fixtures (with the published-digest check). The caption says
  from the data whether pressure-day frequency rises with the state.
* View N5 walks through a quarter-end in steps (#146), on two quarter-ends
  chosen by Eleonora's rule (answer 10 on #141, `N5_QUARTER_END_RULE`) from
  the ON RRP result public at each one's decision instant, never from a spread.
  SOFR's 99th percentile, the EFFR and ON RRP are read from the tracked
  snapshots through the ingest adapter, with its checksum check; the panel
  does not change. Each chart marks what was public at that decision instant.
* The status of each tag on view N4's market map (`docs/visual/map.json`) is
  derived, never typed: from the sources registry, the panel manifest, the
  declarations of the published run records, the tracked fixtures and the
  tracked issue snapshot `docs/visual/issues.json` (#141 §3). Only the
  declarations of a run record are read, never its results. The snapshot is
  written by `--refresh-issues`, the one command here that uses the network;
  generation reads the file and stays byte-reproducible.

Every data file carries a provenance block: the commit, the panel's SHA-256 and
the SHA-256 of each input file read. The commit is the latest one that changed
one of `INPUTS`, never the commit that records the output: a file cannot name
the commit that contains it, so a pull request that changes an input commits
that change first, then runs this script and commits the output on top, as
`scripts/emit_status.py` does. It reads git history, so it refuses a shallow
clone unless the commit is passed with `--commit`.

Standard library only, plus this repository's own `src/`.

    python3 scripts/emit_visual.py            # writes docs/visual/data/ and site/index.html
    python3 scripts/emit_visual.py --check    # writes nothing; fails if either is stale
    python3 scripts/emit_visual.py --refresh-issues   # rewrites docs/visual/issues.json from GitHub
"""
import argparse
import bisect
import csv
import fnmatch
import hashlib
import html
import importlib.util
import json
import math
import re
import statistics
import subprocess
import sys
import tempfile
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model.asof import declared_availability, fold_grid  # noqa: E402
from repo_model.contract import CALENDAR_FEATURES, FEATURE_FIELDS, ON_RRP_DEPLETION_BREAK_BN  # noqa: E402
from repo_model.data import (  # noqa: E402
    QUARTER_END_WINDOW_BUSINESS_DAYS, TAX_DEADLINE_MONTHS, corporate_tax_deadline, exceeds_bp, quarter_end_window)
from repo_model.ingest import (  # noqa: E402
    NYFED_ON_RRP_FIELD,
    NYFED_ON_RRP_SOURCE_ID,
    NYFED_SRF_FIELD,
    NYFED_SRF_SOURCE_ID,
    load_snapshot_manifest,
    parse_snapshots,
)
from repo_model.lockbox import locked_tier, locked_tiers  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402
from repo_model.scarcity import (  # noqa: E402
    BOOTSTRAP_BLOCK_LENGTH,
    BOOTSTRAP_LEVEL,
    BOOTSTRAP_REPLICATIONS,
    BOOTSTRAP_SEED,
    ON_RRP_BUFFER_BN,
    SATIATION_BAND,
    STATE_LABELS,
    measurement_declaration,
    pressure_days_by_state,
    with_reserve_scarcity_state,
)
from repo_model.splits import LookAheadError  # noqa: E402

# #115's measurement panel, loaded from its script by path: scripts/ is not a package.
_spec = importlib.util.spec_from_file_location("scarcity_validation", ROOT / "scripts" / "scarcity_validation.py")
_scarcity_validation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scarcity_validation)
build_measurement_panel = _scarcity_validation.build_measurement_panel

FIXTURES = "tests/fixtures/snapshots/funding_inputs"
MANIFEST = "metadata/funding_panel_manifest.json"
SOURCES = "metadata/sources.json"
EVENTS = "metadata/events.json"
THRESHOLDS = "metadata/stress_thresholds.json"
SPLITS = "metadata/evaluation_splits.json"
LOCKBOX = "metadata/lockbox.json"
HOLIDAYS = "metadata/market_holidays.json"
ON_RRP = "tests/fixtures/snapshots/on_rrp_inputs/nyfed_on_rrp"
H8 = "tests/fixtures/snapshots/h8_inputs/frb_h8"
SOFR_RATES = "tests/fixtures/snapshots/funding_inputs/nyfed-sofr-rate"
EFFR = "tests/fixtures/snapshots/nyfed_effr_inputs/nyfed_effr"
SRF = "tests/fixtures/snapshots/srf_inputs/nyfed_srf"
ANNOTATIONS = "docs/visual/annotations.json"
GLOSSARY = "docs/visual/glossary.json"
MAP = "docs/visual/map.json"
ISSUES = "docs/visual/issues.json"
RUNS = "docs/runs"
#: The final test (#151): the near-blind tier opened once. The site's "Final test" section (#238) reads it alone.
FINAL_TEST = f"{RUNS}/final_test_near_blind.json"
SNAPSHOTS = "tests/fixtures/snapshots"
REPOSITORY = "eleonorabjornberg/repo-market-model"
TEMPLATE = "site/template.html"
#: The use limitation (#261): one statement, read here and by `emit_results.py`.
USE_LIMITATION = "docs/use-limitation.md"
PAGE = "site/index.html"
DATA_DIR = "docs/visual/data"

#: What the commit stamp is the latest change to. Every file the script reads
#: directly, the fixtures the panel is built from, and the script itself.
INPUTS = (
    "scripts/emit_visual.py",
    "scripts/scarcity_validation.py",
    USE_LIMITATION,
    TEMPLATE,
    "docs/visual/annotations.json",
    GLOSSARY,
    "docs/visual/sources",
    MANIFEST,
    SOURCES,
    EVENTS,
    THRESHOLDS,
    SPLITS,
    LOCKBOX,
    HOLIDAYS,
    FIXTURES,
    ON_RRP,
    H8,
    MAP,
    ISSUES,
    FINAL_TEST,
    f":(glob){RUNS}/*.json",
    SNAPSHOTS,
)

#: Run records the model chapters render: one exceedance record per scored
#: model and benchmark. Each passes `require_as_of`, which fails closed.
MODEL_RECORDS = f"{RUNS}/exceedance_*.json"

#: The pressure probability's benchmarks (`docs/decisions/pressure-probability.md`),
#: by the `model` their records declare, in the order the page draws them.
BENCHMARKS = (
    ("calendar_climatology", "Calendar-type climatology"),
    ("persistence_logistic", "Persistence-logistic"),
)

#: A declared `model` as the page names it. A model not listed is refused
#: rather than shown under a guessed name.
MODEL_NAMES = dict(BENCHMARKS, climatology="Climatology", gbm="Gradient-boosted distribution")

#: The pressure-day types a record splits by, as the page names them.
DAY_TYPES = {"month_end": "Month-end", "ordinary": "Ordinary", "quarter_end": "Quarter-end",
             "tax_date": "Tax date"}

#: Model figures that no published record carries yet: (key, the field a record
#: would carry, what the figure shows). While no record in docs/runs/ carries
#: the field, its chapter renders a generated placeholder; once one does, the
#: generator refuses until the figure is drawn from it.
PENDING = (
    ("lead_time", "lead_time", "lead time to the onset of pressure"),
)

#: An order-of-magnitude bound on reserve balances in USD billions, the unit the
#: panel carries since #41. Millions land above it, trillions below it.
RESERVE_BILLIONS = (100.0, 100_000.0)

LOCKBOX_RULE = "https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/decisions/lockbox.md"
BLOB = f"https://github.com/{REPOSITORY}/blob/main/"
CLIP_BP = 45  # top of the full-period scale; days above it are drawn off the frame

#: The newcomer layer's views (#141), in reading order: (section id, title, subtitle).
#: The "Start here" nav lists only those whose section the template carries, so
#: a half-built layer never shows a dead link.
NEWCOMER_VIEWS = (
    ("n1", "What is pressure?", "The line this project watches"),
    ("n2", "Why is this hard?", "Pressure days are rare"),
    ("n3", "When does it happen?", "Scarce cash and the calendar"),
    ("n4", "Who lends to whom", "The market map"),
    ("n5", "A quarter-end squeeze", "Step by step"),
)

#: The minimum history of the published declarations: the scored grid starts at
#: the first row with this many observable labels (`asof.fold_grid`). N2 draws
#: that grid; `tests/test_visual.py` cross-checks it against the fold dates of
#: `docs/runs/persistence_funding.json`, so the generator reads no run record.
N2_MINIMUM_HISTORY = 61

#: A map tag's statuses (#141 §3), in the order the derivation tries them, the
#: first match winning: (key, icon, word). The page shows the icon and the word,
#: never colour alone.
STATUSES = (
    ("used", "\u25cf", "Used"),
    ("tried_and_hurt", "\u2715", "Tried and hurt"),
    ("in_progress", "\u25d0", "In progress"),
    ("registered_unused", "\u25cb", "Registered but unused"),
    ("not_registered", "\u2013", "Not registered"),
)

#: The kinds of flow N4's map draws: (key, legend label, SVG stroke dash). Every
#: arrow points the way the cash goes.
FLOW_KINDS = (
    ("repo", "Repo loan: cash lent overnight against Treasuries", None),
    ("fed_funds", "Unsecured overnight loan (federal funds)", "9 4"),
    ("balance", "Cash kept at the Fed", "2 3"),
    ("settlement", "Payment for Treasuries bought at auction", "7 3 1 3"),
)

#: N4's segment chart (#145, Eleonora's scope of 2 October 2026): the days are
#: chosen from inputs known in advance, never from a spread or any outcome.
#: A day is chosen when it is before `before` and either
#: * a quarter-end (the panel's `quarter_end` flag, the in-force one-day
#:   definition) on which the ON RRP result public at that day's decision
#:   instant (16:00 on the panel day before it) was below `on_rrp_below_bn`; or
#: * a corporate tax deadline (`data.corporate_tax_deadline`) on which Treasury
#:   coupon securities settled (`treasury_settlement_coupons` above zero, a
#:   scheduled input announced before the day).
#: Days in a locked lockbox tier are never chosen.
SEGMENT_DAY_RULE = {"before": "2026-01-01", "on_rrp_below_bn": ON_RRP_DEPLETION_BREAK_BN}
#: The only panel columns the rule reads. tests/test_visual.py runs the rule on
#: rows cut down to these and requires the same days.
SEGMENT_RULE_COLUMNS = ("date", "quarter_end", "treasury_settlement_coupons")
#: The rates the segment chart draws, each less IORB: (panel column, label).
SEGMENTS = (("tgcr", "TGCR"), ("bgcr", "BGCR"), ("sofr", "SOFR"))

#: N5's two worked quarter-ends (Eleonora's answer 10 on #141), chosen from inputs only, never from a
#: spread. Among the quarter-ends before `before` (the panel's `quarter_end` flag) in no locked tier, each
#: read with the ON RRP result public at its decision instant (the declared decision time on the panel day
#: before it, as N4's segment rule reads it):
#: * scarce: the most recent one whose reading is below `scarce_below_bn`;
#: * abundant: the one with the largest reading.
N5_QUARTER_END_RULE = {"before": "2026-01-01", "scarce_below_bn": ON_RRP_DEPLETION_BREAK_BN}
#: The only panel columns the rule reads. tests/test_visual.py runs it on rows cut down to these.
N5_RULE_COLUMNS = ("date", "quarter_end")
#: Business days drawn on either side of each worked quarter-end.
N5_WINDOW_BUSINESS_DAYS = 5
#: The series N5's step charts draw (`steps[].series` in map.json): label, unit ("bn": USD billions; "bp":
#: basis points over IORB), whether the chart draws the level or the change since the window's first day,
#: and the reads, each a panel column or an N5 snapshot series (`N5_SNAPSHOTS`). A "bp" series is its first
#: read less the panel's IORB. `hindsight` marks a latest-vintage level (#141 §2.4).
N5_SERIES = {
    "treasury_settlement": {"label": "Treasury settlements", "unit": "bn", "mode": "level",
                            "reads": [("panel", "treasury_settlement")]},
    "tga": {"label": "Treasury General Account", "unit": "bn", "mode": "change", "reads": [("panel", "tga")],
            "hindsight": True},
    "reserve_balances": {"label": "Reserve balances", "unit": "bn", "mode": "change",
                         "reads": [("panel", "reserve_balances")], "hindsight": True},
    "dealer_treasury_position": {"label": "Dealer Treasury positions", "unit": "bn", "mode": "level",
                                 "reads": [("panel", "dealer_treasury_position")]},
    "on_rrp": {"label": "Overnight reverse repo", "unit": "bn", "mode": "level", "reads": [("snapshot", "on_rrp")]},
    "sofr_p99": {"label": "SOFR's 99th percentile", "unit": "bp", "mode": "level",
                 "reads": [("snapshot", "sofr_p99"), ("panel", "iorb")]},
    "spread": {"label": "SOFR", "unit": "bp", "mode": "level", "reads": [("panel", "sofr"), ("panel", "iorb")]},
    "effr": {"label": "EFFR", "unit": "bp", "mode": "level", "reads": [("snapshot", "effr"), ("panel", "iorb")]},
    "srf": {"label": "Standing repo take-up", "unit": "bn", "mode": "level", "reads": [("snapshot", "srf")]},
}
#: N5's snapshot series: key -> (snapshot directory, source id, adapter series id).
N5_SNAPSHOTS = {
    "on_rrp": (ON_RRP, NYFED_ON_RRP_SOURCE_ID, NYFED_ON_RRP_FIELD),
    "sofr_p99": (SOFR_RATES, "nyfed_sofr", "SOFR_p99"),
    "effr": (EFFR, "nyfed_effr", "EFFR"),
    "srf": (SRF, NYFED_SRF_SOURCE_ID, NYFED_SRF_FIELD),
}

#: An open "Publish?" question about directive N: "Publish? <title> (#N)".
PUBLISH_TITLE = re.compile(r"^Publish\? .*\(#(\d+)\)$")

#: Events from `annotations.json` that N1 marks on its chart, by date.
N1_EPISODES = ("2019-09-17", "2020-03-15", "2022-06-01", "2025-12-01")
TYPES = ["Quarter-end", "Month-end", "Tax window", "Coupon settlement", "Other"]
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve"]
ALLOWED_SOURCES = (
    "https://www.federalreserve.gov/",
    "https://www.newyorkfed.org/",
    "https://tellerwindow.newyorkfed.org/",
    "https://home.treasury.gov/",
    "https://fiscaldata.treasury.gov/",
    "https://github.com/eleonorabjornberg/repo-market-model/",
)
COLUMN_LABELS = {
    "sofr": "SOFR",
    "iorb": "Rate on reserves (IORB, IOER)",
    "sofr_volume": "SOFR volume",
    "sofr_p25": "SOFR 25th percentile",
    "sofr_p75": "SOFR 75th percentile",
    "tgcr": "TGCR",
    "bgcr": "BGCR",
    "reserve_balances": "Reserve balances",
    "tga": "Treasury General Account",
    "on_rrp": "Overnight reverse repo",
    "treasury_settlement": "Treasury settlements, all",
    "treasury_settlement_bills": "Treasury settlements, bills",
    "treasury_settlement_coupons": "Treasury settlements, coupons",
    "treasury_settlement_soma": "Treasury settlements, Fed add-ons",
    "dealer_treasury_position": "Dealer Treasury positions",
    "tbill_4w": "4-week bill yield",
    "tbill_13w": "13-week bill yield",
    "quarter_end": "Quarter-end flag",
    "tax_date": "Tax-date flag",
    "days_to_month_end": "Days to month-end",
}


#: The final test's split by pressure-day type, in the order the section lists it.
FINAL_TEST_DAY_TYPES = ("ordinary", "month_end", "quarter_end", "tax_date")
#: The event cells the section names when it says the test is not a warning of stress.
FINAL_TEST_STRESS_TARGETS = (("+5bp", "+5"), ("+10bp", "+10"))
#: The second amendment's outcome labels (4 October 2026), as `scripts/emit_results.py` renders them.
FINAL_TEST_LABELS = {"pass": "shown better", "not distinguishable": "not shown", "worse": "shown worse"}


class VisualError(ValueError):
    """The page cannot be generated honestly from what is on disk."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(rel, repo):
    return json.loads((repo / rel).read_text(encoding="utf-8"))


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def input_commit(repo):
    """The latest commit that changed one of `INPUTS`."""
    if git(repo, "rev-parse", "--is-shallow-repository") == "true":
        raise VisualError("the clone is shallow, so the latest commit to change an input cannot be "
                          "read; run `git fetch --unshallow` or pass --commit")
    return git(repo, "log", "-1", "--format=%H", "--", *INPUTS)


# ---------------------------------------------------------------- guards


def require_as_of(record, name="record"):
    """Refuse a run record unless every information set in it is the as-of rule.

    Directive 01 records the rule under `derived.information_set.rule`; a
    comparison record carries one per model. A record with none, or with any
    other rule, scored its forecasts under a rule this page does not publish.
    """
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "information_set" and isinstance(value, dict):
                    found.append(value.get("rule"))
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(record)
    if not found:
        raise LookAheadError(f"{name}: declares no information rule; a model chapter renders only "
                             f"records scored under the as-of rule")
    other = sorted({str(rule) for rule in found if rule != "as_of"})
    if other:
        raise LookAheadError(f"{name}: information rule {other} is not the as-of rule; refusing")
    return record


def load_run_record(path):
    return require_as_of(json.loads(Path(path).read_text(encoding="utf-8")), str(path))


def is_published_record(rel):
    """A top-level JSON file in docs/runs/: published, and not archived."""
    rel = str(rel)
    return rel.startswith(RUNS + "/") and "/" not in rel[len(RUNS) + 1:] and rel.endswith(".json")


def from_record(records, rel, *keys):
    """A model figure's value, read from the published record `rel`.

    The only way a model chapter reads a number. It refuses a path outside
    docs/runs/, a record that is not there, and a field the record lacks, so no
    figure is drawn without a published record behind it.
    """
    if not is_published_record(rel):
        raise VisualError(f"{rel}: a model figure reads only a published record in {RUNS}/")
    if rel not in records:
        raise VisualError(f"no published record {rel}: refusing a figure without one")
    node = records[rel]
    for i, key in enumerate(keys):
        if not isinstance(node, dict) or key not in node:
            raise VisualError(f"{rel} carries no {'.'.join(map(str, keys[:i + 1]))}: refusing a figure "
                              f"without a record")
        node = node[key]
    return node


def pending_figures(records):
    """The generated placeholder for each `PENDING` figure no published record carries.

    A record that carries one is refused: the chapter must draw it, not keep a
    placeholder that says no record exists.
    """

    def carries(node, marker):
        if isinstance(node, dict):
            return any(key == marker or carries(value, marker) for key, value in node.items())
        if isinstance(node, list):
            return any(carries(value, marker) for value in node)
        return node == marker

    out = {}
    for key, marker, what in PENDING:
        carriers = sorted(rel for rel, record in records.items() if carries(record, marker))
        if carriers:
            raise VisualError(f"{carriers[0]} carries {marker}, but the page draws no figure of {what} "
                              f"yet: draw it from the record rather than publish a placeholder")
        out[key] = (f"No published record in <code>{RUNS}/</code> carries {what}, so this page draws "
                    f"no figure of it. The generator draws model figures only from such a record, and "
                    f"refuses one that no record carries.")
    return out


def check_reserve_units(rows):
    """Refuse a panel whose reserve balances are not in USD billions."""
    values = [float(r["reserve_balances"]) for r in rows if r.get("reserve_balances")]
    if not values:
        raise VisualError("the panel carries no reserve balances")
    low, high = min(values), max(values)
    if low < RESERVE_BILLIONS[0] or high >= RESERVE_BILLIONS[1]:
        raise VisualError(f"reserve_balances spans {low:,.3f} to {high:,.3f}, outside "
                          f"{RESERVE_BILLIONS[0]:,.0f} to {RESERVE_BILLIONS[1]:,.0f}: the panel is "
                          f"not in USD billions; refusing rather than rescaling")


def check_annotations(notes):
    """Every annotation names a primary source."""
    entries = list(notes["events"]) + list(notes["runoff"]) + list(notes["process"])
    entries += list(notes["guards"]) + [notes["validation"], notes["implementation_note"]]
    entries += list(notes["claims"].values())
    for entry in entries:
        src = entry.get("src", "")
        if not any(src.startswith(prefix) for prefix in ALLOWED_SOURCES):
            raise VisualError(f"annotation {entry} has no primary-source URL")


def check_glossary(glossary):
    """Every glossary term has a unique key, a printed form, a definition and a primary source."""
    seen = set()
    for entry in glossary["terms"]:
        key = entry.get("key", "")
        if not re.fullmatch(r"\w+", key) or key in seen:
            raise VisualError(f"glossary entry {entry} has no unique key")
        seen.add(key)
        for field in ("term", "text", "definition"):
            if not str(entry.get(field, "")).strip():
                raise VisualError(f"glossary term {key!r} has no {field}")
        if not entry.get("match"):
            raise VisualError(f"glossary term {key!r} lists no pattern")
        if not any(str(entry.get("src", "")).startswith(prefix) for prefix in ALLOWED_SOURCES):
            raise VisualError(f"glossary term {key!r} has no primary-source URL")


def dfn_fills(glossary):
    """`{{dfn_<key>}}`: the term as a <dfn>, with a keyboard-reachable disclosure for its definition.

    The definition is in the page, not in a `title`: the term is an inline
    control (`role="button"`, in the tab order) that toggles it by tap, Enter or
    Space, and Esc closes it. A <button> would let a line break open beside the
    term and strand the punctuation after it.
    """
    out = {}
    for entry in glossary["terms"]:
        key = entry["key"]
        out[f"dfn_{key}"] = (
            f'<dfn id="term-{key}" data-term="{key}"><span class="term" role="button" tabindex="0" aria-expanded="false" '
            f'aria-controls="def-{key}">{html.escape(entry["text"])}</span></dfn>'
            f'<span class="def" id="def-{key}" role="note" hidden> <b>{html.escape(entry["term"])}:</b> '
            f'{html.escape(entry["definition"])} <a href="{entry["src"]}">Source</a></span><!--/def-->')
    return out


def newcomer_nav(template):
    """The "Start here" nav: the views the template carries, in reading order."""
    items = "".join(
        f'<li class="live"><b>N{i}</b><span><a href="#{sid}">{title}</a><small>{sub}</small></span></li>'
        for i, (sid, title, sub) in enumerate(NEWCOMER_VIEWS, 1) if f'<section id="{sid}"' in template)
    return f"<ol>{items}</ol>"


def use_limitation_fill(repo):
    """`{{use_limitation}}`: the one blockquote line of `docs/use-limitation.md` (#261)."""
    text = (Path(repo) / USE_LIMITATION).read_text(encoding="utf-8")
    found = [line[2:].strip() for line in text.splitlines() if line.startswith("> ")]
    if len(found) != 1 or not found[0]:
        raise VisualError(f"{USE_LIMITATION} must carry exactly one blockquote line, the statement; "
                          f"found {len(found)}")
    return {"use_limitation": html.escape(found[0], quote=False)}


def fill(template, fills):
    """Fill `{{name}}` placeholders; any left over is an error."""
    out = template
    for key, value in fills.items():
        out = out.replace("{{" + key + "}}", str(value))
    left = sorted(set(re.findall(r"\{\{\w+\}\}", out)))
    if left:
        raise VisualError(f"unfilled placeholders: {left}")
    return out


# ---------------------------------------------------------------- panel


def build_panel(repo, manifest, workdir):
    out = Path(workdir) / "funding_panel.csv"
    cmd = [sys.executable, "-m", "repo_model.cli", "build", "--raw-root", FIXTURES,
           "--output", str(out), "--build-cutoff", manifest["build_cutoff"],
           "--decision-time", manifest["decision_time"]]
    env = {"PYTHONPATH": str(repo / "src"), "PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
    done = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, env=env)
    if done.returncode:
        raise VisualError(f"panel build failed: {done.stderr.strip()[-400:]}")
    digest = sha256(out)
    if digest != manifest["sha256"]:
        raise VisualError(f"panel digest {digest[:12]} is not the published {manifest['sha256'][:12]}; "
                          f"refusing")
    return out.read_bytes(), digest


# ---------------------------------------------------------------- formatting


def day(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def short_day(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def span(a, b):
    x, y = date.fromisoformat(a), date.fromisoformat(b)
    return f"{x.day}–{day(b)}" if (x.year, x.month) == (y.year, y.month) else f"{day(a)} – {day(b)}"


def of(k, n):
    return f"{k} of {n} ({round(100 * k / n)}%)" if n else "no days"


def days(n):
    return f"{n} day" if n == 1 else f"{n} days"


def dash(label):
    return label.replace("-", "–")


def lower_first(label):
    """'Dealer Treasury positions' -> 'dealer Treasury positions'; acronyms such as 'SOFR' stay."""
    return label if label[1:2].isupper() else label[:1].lower() + label[1:]


def word(n):
    return NUMBER_WORDS[n] if 0 <= n < len(NUMBER_WORDS) else str(n)


def bp(value):
    return f"{'+' if value > 0 else '−' if value < 0 else ''}{abs(value)}"


def clock(t):
    h, m = t.hour, t.minute
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return f"{h12}{'' if m == 0 else ':%02d' % m} {suffix}"


def link(claim):
    return f"{claim['text']} (<a href='{claim['src']}'>source</a>)."


def held_as(names):
    """What held-out days are: the locked tiers they fall in, which no test has opened (`docs/decisions/lockbox.md`)."""
    tiers = list(dict.fromkeys(n.replace("_", "-") for n in names))
    what = (f"the {tiers[0]} tier" if len(tiers) == 1 else
            "the " + " and ".join(tiers) + " tiers")
    return f"held out as {what}, which no test has opened (<a href='{LOCKBOX_RULE}'>the lockbox rule</a>)"


def signed(value, places):
    """A signed figure as the page prints it, with a true minus sign: '+0.5', '−0.5'."""
    text = f"{abs(value):.{places}f}"
    if float(text) == 0:
        return text
    return ("+" if value > 0 else "−") + text


# ---------------------------------------------------------------- chapter 1


def parse_note(repo, meta):
    """The rates the implementation note states, parsed from its checksummed bytes."""
    path = repo / meta["path"]
    if sha256(path) != meta["sha256"]:
        raise VisualError(f"{meta['path']} does not match its recorded SHA-256; refusing")
    raw = path.read_bytes().decode("utf-8-sig")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)))

    def find(pattern, what):
        m = re.search(pattern, text)
        if not m:
            raise VisualError(f"the implementation note does not state {what}")
        return m.groups()

    def mixed(s):  # "3-3/4" -> 3.75, "4" -> 4
        whole, _, frac = s.strip().partition("-")
        value = Decimal(whole)
        if frac:
            num, den = frac.split("/")
            value += Decimal(num) / Decimal(den)
        return value

    def iso(s):
        return datetime.strptime(s, "%B %d, %Y").date().isoformat()

    issued, = find(r"Implementation Note issued (\w+ \d{1,2}, \d{4})", "its issue date")
    effective, = find(r"Effective (\w+ \d{1,2}, \d{4}), the Federal Open Market Committee directs",
                      "an effective date")
    lo, hi = find(r"target range of ([\d\-/]+) to ([\d\-/]+) percent", "the target range")
    iorb, = find(r"interest rate paid on reserve balances (?:to|at) ([\d.]+) percent", "IORB")
    srp, = find(r"standing overnight repurchase agreement operations at a (?:minimum bid )?rate of "
                r"([\d.]+) percent", "the standing repo rate")
    rrp, = find(r"standing overnight reverse repurchase agreement operations at an offering rate of "
                r"([\d.]+) percent", "the overnight reverse repo rate")
    pcr, = find(r"primary credit rate (?:to|at) ([\d.]+) percent", "the primary credit rate")
    iorb_d = Decimal(iorb)
    rates = [
        {"key": "srp", "name": "Standing repo rate", "who": "Dealers and banks borrow cash from the Fed",
         "v": Decimal(srp)},
        {"key": "pcr", "name": "Primary credit rate", "who": "Banks borrow at the discount window",
         "v": Decimal(pcr)},
        {"key": "iorb", "name": "IORB", "who": "Banks earn it on their reserves", "v": iorb_d},
        {"key": "rrp", "name": "Overnight reverse repo rate",
         "who": "Money funds and other non-banks lend cash to the Fed", "v": Decimal(rrp)},
    ]
    for r in rates:
        r["vs_iorb_bp"] = int((r["v"] - iorb_d) * 100)
        r["v"] = float(r["v"])
    return {
        "issued": iso(issued), "effective": iso(effective),
        "range": [float(mixed(lo)), float(mixed(hi))],
        "rates": rates, "src": meta["src"], "sha256": meta["sha256"],
        "retrieved_at": meta["retrieved_at"],
    }


# ---------------------------------------------------------------- chapter 4


def publication_clock(registry, columns, decision):
    """Each panel input's publication instant relative to the day its value describes.

    Read through `asof.declared_availability`, the same function the as-of rule
    uses, on a synthetic run of consecutive days so that one row is one day.
    """
    dates = [date(2001, 1, 1) + timedelta(days=i) for i in range(60)]
    pos = 30
    origin = datetime.combine(dates[pos], time.min)
    out = []
    for column in columns:
        label = COLUMN_LABELS.get(column, column)
        if column in CALENDAR_FEATURES:
            out.append({"column": column, "label": label, "kind": "calendar"})
            continue
        seen = {}
        for source_id, field in FEATURE_FIELDS[column]:
            source = registry[source_id]
            scheduled = source.get("scheduled_availability") or {}
            if field in (scheduled.get("fields") or ()):
                decl, kind = scheduled, "scheduled"
            else:
                decl = (source.get("field_release_lags") or {}).get(field) or source["release_lag"]
                kind = "retrieval" if decl.get("basis") == "snapshot_retrieved_at" else "observed"
            at = declared_availability(registry, source_id, field, dates, pos)
            key = (kind, decl.get("days"), decl.get("unit"), decl.get("available_time"))
            if key in seen:
                seen[key]["fields"].append(field)
                continue
            entry = {"column": column, "label": label, "kind": kind, "source": source_id,
                     "provider": source.get("provider", source_id), "fields": [field],
                     "unit": decl.get("unit"), "days": decl.get("days"),
                     "time": decl.get("available_time")}
            if at is not None:
                offset = (at - origin) / timedelta(days=1)
                entry["offset"] = round(offset, 4)
                whole = math.floor(offset)
                late = at.time() > decision
                entry["read_lag"] = whole + (1 if late else 0)
            seen[key] = entry
        out.extend(seen.values())
    return out


# ---------------------------------------------------------------- chapters 2 and 3


def counted(rows, locked):
    """The rows a count, share, median or sentence may use: none in a locked tier.

    `locked` is `lockbox.locked_tiers(...)`: the tiers not yet opened. The rows
    left out are still drawn, greyed and labelled "held out".
    """
    return [r for r in rows if locked_tier(date.fromisoformat(r["date"]), locked) is None]


def held_out_spans(rows, locked):
    """Each locked tier that holds panel days, clamped to the panel's last day."""
    last = rows[-1]["date"]
    spans = []
    for tier in locked:
        start, end = tier.start.isoformat(), min(tier.end.isoformat() if tier.end else last, last)
        if any(start <= r["date"] <= end for r in rows):
            spans.append({"name": tier.name, "start": start, "end": end})
    return spans


def period_label(g, rows, kept):
    """A regime's label, narrowed to what is counted when held-out days fall inside it.

    "2025-26" becomes "2025" when only 2025 days are counted, and states the
    last counted day when held-out days share its year.
    """
    inside = [r["date"] for r in rows if g["first"] <= r["date"] <= g["last"]]
    used = [r["date"] for r in kept if g["first"] <= r["date"] <= g["last"]]
    if len(used) == len(inside):
        return dash(g["label"])
    y0, y1 = used[0][:4], used[-1][:4]
    label = y0 if y0 == y1 else f"{y0}–{y1[2:]}"
    if any(d[:4] == y1 for d in set(inside) - set(used)):
        label += f" (to {short_day(used[-1])})"
    return label


def classify(rows):
    for i, r in enumerate(rows):
        if i + 1 < len(rows):
            nxt = rows[i + 1]["date"]
        else:  # the panel's last row: its successor is not in the panel, so use the next weekday
            d = date.fromisoformat(r["date"])
            nxt = (d + timedelta(days=3 if d.weekday() == 4 else 1)).isoformat()
        last_bd = nxt[5:7] != r["date"][5:7]
        if r["quarter_end"] == "1":
            r["t"] = 0
        elif last_bd:
            r["t"] = 1
        elif r["tax_date"] == "1":
            r["t"] = 2
        elif float(r["treasury_settlement_coupons"]) > 0:
            r["t"] = 3
        else:
            r["t"] = 4


def regime_views(regimes, rows, clip_bp, second_bp):
    first, last = rows[0]["date"], rows[-1]["date"]
    floor = max(-25, 5 * math.floor(min(r["s"] for r in rows) / 5))
    views = [{"k": "all", "label": "All years", "x": [first, last], "y": [floor, clip_bp]}]
    for g in regimes:
        lo, hi = max(g["first"], first), min(g["last"], last)
        inside = sorted(r["s"] for r in rows if lo <= r["date"] <= hi)
        if not inside:
            continue
        top = inside[min(len(inside) - 1, math.ceil(0.995 * len(inside)) - 1)]
        views.append({"k": g["label"], "label": dash(g["label"]), "x": [lo, hi],
                      "y": [5 * math.floor((inside[0] - 2) / 5), max(second_bp + 5, 10 * math.ceil((top + 5) / 10))]})
    return views


def history(rows, notes, thresholds, regimes, windows, locked):
    taus = [int(t) for t in thresholds["taus_bp"]]
    pressure_bp, second_bp, tail_bp = taus[0], taus[1], taus[-1]
    out_rows = []
    for r in rows:
        iorb = Decimal(r["iorb"])
        r["s"] = int((Decimal(r["sofr"]) - iorb) * 100)
        r["res"] = float(r["reserve_balances"]) / 1e3  # USD billions -> trillions, for the axis
    classify(rows)
    kept = counted(rows, locked)
    for r in rows:
        iorb = Decimal(r["iorb"])
        band = [None, None]
        if r["sofr_p25"] and r["sofr_p75"]:
            band = [int((Decimal(r["sofr_p25"]) - iorb) * 100), int((Decimal(r["sofr_p75"]) - iorb) * 100)]
        out_rows.append([r["date"], r["s"], band[0], band[1], float(r["sofr"]), float(iorb),
                         round(r["res"], 3), r["t"]])

    def in_regime(r, g):
        return g["first"] <= r["date"] <= g["last"]

    def pressure(r):
        return r["s"] > pressure_bp

    def med(g):
        return round(statistics.median(r["res"] for r in kept if in_regime(r, g) and pressure(r)), 2)

    def type_count(g, t):
        n = [r for r in kept if in_regime(r, g) and r["t"] == t]
        return sum(1 for r in n if pressure(r)), len(n)

    live = [g for g in regimes if any(in_regime(r, g) for r in kept)]
    early, late = live[0], live[-1]
    ample = max(live, key=lambda g: statistics.median(r["res"] for r in kept if in_regime(r, g)))
    label = {g["label"]: period_label(g, rows, kept) for g in live}
    yr = lambda r: int(r["date"][:4])
    years = list(range(yr(rows[0]), yr(rows[-1]) + 1))
    counted_years = {yr(r) for r in kept}
    held_years = {yr(r) for r in rows} - counted_years
    kept_days = {r["date"] for r in kept}
    partial = {yr(r) for r in rows if r["date"] not in kept_days} & counted_years  # counted only in part
    cells = {(y, t): [0, 0] for y in years for t in range(len(TYPES))}
    for r in kept:
        c = cells[(yr(r), r["t"])]
        c[0] += 1
        c[1] += pressure(r)

    def th(y):
        if y in held_years:
            return f"<th scope='col' class='held'>{y}<br>held out</th>"
        to = max(r["date"] for r in kept if yr(r) == y)
        return f"<th scope='col'>{y}{' (to ' + short_day(to)[:-5] + ')' if y == years[-1] or y in partial else ''}</th>"

    head = "".join(th(y) for y in years)
    body = []
    for t, name in enumerate(TYPES):
        tds = []
        for y in years:
            if y in held_years:
                tds.append("<td class='held'>held out</td>")
                continue
            n, k = cells[(y, t)]
            share = k / n if n else 0
            cls = " class='hot'" if share > 0.5 else ""
            tds.append(f"<td{cls} style='--share:{round(100 * share)}%'><b>{k}</b><span> of {n}</span></td>")
        body.append(f"<tr><th scope='row'>{name}</th>{''.join(tds)}</tr>")
    table = f"<table><thead><tr><th></th>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"

    held = held_out_spans(rows, locked)
    held_from = " and ".join(f"from {day(h['start'])} to {day(h['end'])}" for h in held)
    spike = max(kept, key=lambda r: r["s"])
    tail = [r for r in kept if r["s"] > tail_bp]
    tail_years = sorted({yr(r) for r in tail})
    events = [{"date": e["date"], "src": e["src"],
               "text": e["text"].format(spike_sofr=f"{float(spike['sofr']):.2f}%", spike_bp=spike["s"])}
              for e in notes["events"]]
    iorb_from = next(e["date"] for e in notes["events"] if e.get("role") == "iorb_from")
    late_qe = type_count(late, 0)
    quiet = all(type_count(ample, t)[0] == 0 for t in range(len(TYPES)))
    off = sum(1 for r in kept if r["s"] > CLIP_BP)
    above = lambda g: sum(1 for r in kept if in_regime(r, g) and r["s"] > 0)
    span_years = (date.fromisoformat(rows[-1]["date"]) - date.fromisoformat(rows[0]["date"])).days / 365.25
    fills = {
        "n_years_word": word(int(span_years)).capitalize(),
        "early": label[early["label"]], "late": label[late["label"]], "ample": label[ample["label"]],
        "above_ample": days(above(ample)), "above_late": days(above(late)),
        "pressure_bp": pressure_bp, "second_bp": second_bp, "tail_bp": tail_bp,
        "n_tail": days(len(tail)),
        "tail_where": ("all in " + str(tail_years[0]) if len(tail_years) == 1 else
                       "all in " + f"{tail_years[0]}–{str(tail_years[1])[2:]}" if len(tail_years) == 2 and tail_years[1] - tail_years[0] == 1
                       else "in " + ", ".join(map(str, tail_years))) if tail_years else "none",
        "spike_bp": bp(spike["s"]), "spike_day": day(spike["date"]),
        "spike_month": date.fromisoformat(spike["date"]).strftime("%B %Y"),
        "med_early": f"${med(early):.2f} trillion", "med_late": f"${med(late):.2f} trillion",
        "ord_early": of(*type_count(early, 4)), "ord_late": of(*type_count(late, 4)),
        "qe_late": f"{late_qe[0]} of {late_qe[1]}",
        "quiet_ample": "there were none" if quiet else "there were a few",
        "band_missing": days(sum(1 for r in kept if not (r["sofr_p25"] and r["sofr_p75"]))),
        "holdouts": " and ".join(span(w["start"], w["end"]) for w in windows),
        "holdout_months": " and ".join(date.fromisoformat(w["start"]).strftime("%B %Y") for w in windows),
        "iorb_from": day(iorb_from),
        "iorb_event_n": 1 + next(i for i, e in enumerate(notes["events"]) if e.get("role") == "iorb_from"),
        "ioer_until": day((date.fromisoformat(iorb_from) - timedelta(days=1)).isoformat()),
        "heat_table": table, "clip_bp": CLIP_BP,
        "n_off_scale": days(off).capitalize(), "n_off_scale_lc": days(off),
        "event_list": "".join(
            f"<li data-i='{i}'><time>{short_day(e['date'])}</time> {e['text']}. <a href='{e['src']}'>Source</a></li>"
            for i, e in enumerate(events)),
        "c_reserve_ratio": link(notes["claims"]["reserve_ratio"]),
        "c_quarter_end": link(notes["claims"]["quarter_end"]),
        "c_tax_date": link(notes["claims"]["tax_date"]),
        "c_settlement": link(notes["claims"]["settlement"]),
        "c_coupon_demand": link(notes["claims"]["coupon_demand"]),
        "held_out_note": (
            "<p class='note'>Grey, labelled “held out”: the days " + held_from
            + ", " + held_as(h["name"] for h in held) + ". "
            "These days are drawn but not coloured, counted or described anywhere on this page.</p>") if held else "",
        "held_out_dots": " Grey dots: held-out days, not counted." if held else "",
        "held_out_footer": (
            " The days " + held_from + " are " + held_as(h["name"] for h in held)
            + ": they are drawn greyed and left out of every count, median and sentence.") if held else "",
    }
    data = {
        "rows": out_rows, "types": TYPES, "events": events,
        "runoff": [{"start": b["start"], "end": b["end"]} for b in notes["runoff"]],
        "holdouts": [{"start": w["start"], "end": w["end"]} for w in windows],
        "medians": [{"label": label[early["label"]], "v": med(early)}, {"label": label[late["label"]], "v": med(late)}],
        "held_out": held,
        "views": regime_views(regimes, rows, CLIP_BP, second_bp),
        "res_domain": [math.floor(10 * min(r["res"] for r in rows)) / 10, math.ceil(10 * max(r["res"] for r in rows)) / 10],
        "iorb_from": iorb_from, "pressure_bp": pressure_bp, "second_bp": second_bp, "clip_bp": CLIP_BP,
    }
    return data, fills


# ---------------------------------------------------------------- chapters 5 and 6


def run_records(repo):
    """{relative path: content} for every published record: each top-level JSON file in docs/runs/."""
    return {f"{RUNS}/{p.name}": json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((Path(repo) / RUNS).glob("*.json"))}


def model_label(declaration, rel):
    model = declaration.get("model")
    if model not in MODEL_NAMES:
        raise VisualError(f"{rel}: no page name for the model {model!r}; refusing to guess one")
    parts = [MODEL_NAMES[model]]
    if declaration.get("calibration"):
        parts.append(declaration["calibration"].replace("_", "-"))
    if model == "gbm":
        parts.append(f"{len(declaration['features'])} inputs")
    return ", ".join(parts)


def thin_curve(points):
    """A CORP curve's points without those inside a flat run, so the drawn line is unchanged."""
    keyed = [tuple(p[k] for k in ("forecast", "recalibrated", "lower", "upper")) for p in points]
    keep = [k for i, k in enumerate(keyed)
            if i in (0, len(keyed) - 1) or k[1:] != keyed[i - 1][1:] or k[1:] != keyed[i + 1][1:]]
    return [[None if v is None else round(v, 5) for v in k] for k in keep]


def model_chapters(records, taus):
    """Chapters 5 and 6, from the published exceedance records alone.

    Every number is read through `from_record`. The scored models are the
    records whose model is not a benchmark; each is drawn against both
    benchmarks, paired, with its interval, by regime and by pressure-day type.
    """
    found = sorted(rel for rel in records if fnmatch.fnmatchcase(rel, MODEL_RECORDS))
    if not found:
        raise VisualError(f"no {MODEL_RECORDS} record: the model chapters have nothing to draw from")
    keys = {}
    for rel in found:
        require_as_of(from_record(records, rel), rel)
        keys[rel] = (from_record(records, rel, "panel", "sha256"), from_record(records, rel, "folds", "count"),
                     from_record(records, rel, "folds", "first", "scored_date"),
                     from_record(records, rel, "folds", "last", "scored_date"))
    if len(set(keys.values())) != 1:
        raise VisualError(f"the exceedance records are not scored on one panel and one set of days: {keys}")
    panel, n_days, first, last = keys[found[0]]
    names = dict(BENCHMARKS)
    tau_keys = [f"{float(t):g}" for t in taus]
    models = []
    for rel in found:
        declaration = from_record(records, rel, "declaration")
        model = declaration.get("model")
        entry = {"record": rel, "label": model_label(declaration, rel), "benchmark": model in names,
                 "inputs": [COLUMN_LABELS.get(f, f) for f in from_record(records, rel, "declaration", "features")],
                 "by_tau": {}}
        for k in tau_keys:
            row = ("metrics", "by_tau", k)
            decomposition = row + ("decomposition",)
            t = {
                "brier": from_record(records, rel, *row, "brier"),
                "base_rate": from_record(records, rel, *row, "base_rate"),
                "positives": from_record(records, rel, *row, "positives"),
                "reliability": from_record(records, rel, *decomposition, "reliability"),
                "resolution": from_record(records, rel, *decomposition, "resolution"),
                "uncertainty": from_record(records, rel, *decomposition, "uncertainty"),
                "curve": thin_curve(from_record(records, rel, *row, "reliability_curve", "points")),
                "vs": {},
            }
            if from_record(records, rel, *row, "reliability_curve", "method") != "corp_isotonic":
                raise VisualError(f"{rel}: the reliability curve at {k} bp is not CORP")
            if not entry["benchmark"]:
                for name, _ in BENCHMARKS:
                    paired = ("benchmarks", name, "by_tau", k, "paired_brier_difference")
                    vs = {"mean": from_record(records, rel, *paired, "mean"),
                          "lower": from_record(records, rel, *paired, "interval", "lower"),
                          "upper": from_record(records, rel, *paired, "interval", "upper"),
                          "level": from_record(records, rel, *paired, "interval", "level"),
                          "benchmark_brier": from_record(records, rel, "benchmarks", name, "by_tau", k,
                                                         "benchmark_brier")}
                    for split, label in (("by_regime", dash), ("by_day_type", None)):
                        groups = from_record(records, rel, *paired, "splits", split)
                        out = []
                        for group in groups:
                            if label is None and group not in DAY_TYPES:
                                raise VisualError(f"{rel}: no page name for the day type {group!r}")
                            g = paired + ("splits", split, group)
                            out.append([label(group) if label else DAY_TYPES[group],
                                        from_record(records, rel, *g, "count"), from_record(records, rel, *g, "mean"),
                                        from_record(records, rel, *g, "interval", "lower"),
                                        from_record(records, rel, *g, "interval", "upper")])
                        vs[split] = out
                    t["vs"][name] = vs
            entry["by_tau"][k] = t
        models.append(entry)
    labels = [m["label"] for m in models]
    if len(set(labels)) != len(labels):
        raise VisualError(f"two exceedance records share a page name: {labels}")
    scored = [m for m in models if not m["benchmark"]]
    if not scored:
        raise VisualError("every exceedance record is a benchmark: no scored model to draw")
    levels = {vs["level"] for m in scored for t in m["by_tau"].values() for vs in t["vs"].values()}
    if len(levels) != 1:
        raise VisualError(f"the paired intervals are not at one level: {sorted(levels)}")
    level = round(100 * levels.pop())

    def beats(k, n, first_clause):
        if k == 0:
            return f"none of the {word(n)} scored models beats" if first_clause else "none beats"
        if k == n:
            return f"all {word(n)} scored models beat" if first_clause else f"all {word(n)} beat"
        verb = "beats" if k == 1 else "beat"
        return f"{word(k)} of the {word(n)} scored models {verb}" if first_clause else f"{word(k)} {verb}"

    def tally(k):
        return [sum(1 for m in scored if m["by_tau"][k]["vs"][name]["lower"] > 0) for name, _ in BENCHMARKS]

    (_, cal_label), (_, per_label) = BENCHMARKS
    sentences = []
    for i, k in enumerate(tau_keys):
        a, b = tally(k)
        sentences.append(f"At +{k} bp, {beats(a, len(scored), i == 0)} {lower_first(cal_label)}"
                         f"{f' with a {level}% interval above zero' if i == 0 else ''}, and "
                         f"{beats(b, len(scored), False)} the {lower_first(per_label)}.")
    k0 = tau_keys[0]
    share = sorted((m["by_tau"][k0]["reliability"] / m["by_tau"][k0]["brier"], m["label"]) for m in models)
    data = {
        "taus": tau_keys, "level": level,
        "benchmarks": [{"key": name, "label": label} for name, label in BENCHMARKS],
        "scored": {"days": n_days, "first": first, "last": last, "panel": panel},
        "models": models,
    }
    fills = {
        "forecast_lede": " ".join(sentences),
        "n_scored_models": word(len(scored)), "n_models": word(len(models)),
        "model_days": f"{n_days:,}", "model_first": day(first), "model_last": day(last),
        "interval_level": level, "tau_first": k0, "tau_second": tau_keys[-1],
        "base_first": f"{100 * models[0]['by_tau'][k0]['base_rate']:.1f}%",
        "miscal_low": f"{100 * share[0][0]:.0f}%", "miscal_low_model": lower_first(share[0][1]),
        "miscal_high": f"{100 * share[-1][0]:.0f}%", "miscal_high_model": lower_first(share[-1][1]),
    }
    if len({m["by_tau"][k0]["base_rate"] for m in models}) != 1:
        raise VisualError("the exceedance records disagree on how often pressure came")
    return data, fills


# ---------------------------------------------------------------- the newcomer layer (#141)


def cluster_years(by_year):
    """The fewest years that hold more than half of the days, listed in date order.

    Years are taken by count, most first (the earlier year on a tie), until
    together they hold more than half; the rule reads only the counts.
    """
    total = sum(by_year.values())
    if not total:
        return []
    picked, held = [], 0
    for year, k in sorted(by_year.items(), key=lambda kv: (-kv[1], kv[0])):
        picked.append(year)
        held += k
        if 2 * held > total:
            break
    return sorted(picked)


def year_list(years):
    years = [str(y) for y in years]
    return years[0] if len(years) == 1 else ", ".join(years[:-1]) + " and " + years[-1]


def newcomer_n1(rows, locked, thresholds, notes):
    """N1 "What is pressure?": what the page says about SOFR − IORB, from unlocked days only.

    The chart draws every panel day from the history series; days in a lockbox
    tier not yet opened are drawn grey and labelled "held out". Every count,
    share and sentence here is computed from `counted(rows, locked)`, the same
    reader chapters 2 and 3 use, so a locked day's value cannot move anything
    this view writes.
    """
    pressure_bp = int(thresholds["taus_bp"][0])
    kept = counted(rows, locked)
    if not kept:
        raise VisualError("every panel day is held out; N1 has nothing to count")
    for r in kept:
        r["n1_s"] = int((Decimal(r["sofr"]) - Decimal(r["iorb"])) * 100)
    hot = [r for r in kept if r["n1_s"] > pressure_bp]
    by_year = {}
    for r in hot:
        by_year[int(r["date"][:4])] = by_year.get(int(r["date"][:4]), 0) + 1
    at_or_below = sum(1 for r in kept if r["n1_s"] <= 0)
    off = [r for r in kept if r["n1_s"] > CLIP_BP]
    spike = max(kept, key=lambda r: r["n1_s"])
    iorb_from = next(e["date"] for e in notes["events"] if e.get("role") == "iorb_from")
    by_date = {e["date"]: e for e in notes["events"]}
    missing = [d for d in N1_EPISODES if d not in by_date]
    if missing:
        raise VisualError(f"N1 marks events {missing} that annotations.json does not carry")
    episodes = [{"date": d, "src": by_date[d]["src"],
                 "text": by_date[d]["text"].format(spike_sofr=f"{float(spike['sofr']):.2f}%",
                                                   spike_bp=spike["n1_s"])}
                for d in N1_EPISODES if locked_tier(date.fromisoformat(d), locked) is None]
    spans = held_out_spans(rows, locked)
    clusters = cluster_years(by_year)
    rest = sorted(set(by_year) - set(clusters))
    data = {
        "held_out": spans, "pressure_bp": pressure_bp, "clip_bp": CLIP_BP, "iorb_from": iorb_from,
        "episodes": episodes,
        "counted": {"first": kept[0]["date"], "last": kept[-1]["date"], "n": len(kept),
                    "pressure": len(hot), "at_or_below_zero": at_or_below, "off_scale": len(off),
                    "by_year": {str(y): k for y, k in sorted(by_year.items())},
                    "cluster_years": clusters},
    }
    fills = {
        "n1_first": day(kept[0]["date"]), "n1_last": day(kept[-1]["date"]),
        "n1_pressure_of": f"{len(hot):,} of the {len(kept):,}",
        "n1_clusters": (f"Most of those days came in {year_list(clusters)}" if clusters else "There were none")
                       + (f"; the rest in {year_list(rest)}." if rest else "."),
        "n1_at_or_below": f"{at_or_below:,} of the {len(kept):,} days counted here "
                          f"({round(100 * at_or_below / len(kept))}%)",
        "n1_off_scale": days(len(off)),
        "n1_spike": f"{bp(spike['n1_s'])} bp on {day(spike['date'])}",
        "n1_src_triparty": notes["claims"]["triparty_actors"]["src"],
        "n1_held_note": (f"Days from {day(spans[0]['start'])} on are {held_as(h['name'] for h in spans)}. "
                         f"They are drawn in grey, labelled "
                         f"&ldquo;held out&rdquo;, and left out of every count and sentence in this view."
                         if spans else "No day on this chart is held out."),
        "n1_iorb_from": day(iorb_from),
        "n1_episode_list": "".join(
            f"<li><time>{short_day(e['date'])}</time> {e['text']}. <a href='{e['src']}'>Source</a></li>"
            for e in episodes),
    }
    return data, fills

# ---------------------------------------------------------------- N4: the tag-status engine (#141 §3, #144)


def pair_name(pair):
    return f"{pair['source']}.{pair['field']}"


def check_map(tag_map, registry, notes):
    """Refuse a map that names a flow, a claim or a registry field it cannot back.

    Every flow, and every board of market-wide series under a party, rests on a
    sourced claim in `annotations.json`. Every tag sits on a flow or a board
    and names (source, field) pairs. A pair the registry lacks is refused
    unless the map marks it `expect: "unregistered"`; such a pair is refused once
    the registry carries it, so a directive that registers the field forces the
    map to be revisited.
    """
    for key, flow in tag_map["flows"].items():
        claim = notes["claims"].get(flow.get("claim"))
        if claim is None:
            raise VisualError(f"map flow {key!r} rests on no claim in {ANNOTATIONS}")
        if not any(claim["src"].startswith(prefix) for prefix in ALLOWED_SOURCES):
            raise VisualError(f"map flow {key!r}: its claim has no primary-source URL")
    for key, board in tag_map.get("boards", {}).items():
        claim = notes["claims"].get(board.get("claim"))
        if claim is None or not any(claim["src"].startswith(prefix) for prefix in ALLOWED_SOURCES):
            raise VisualError(f"map board {key!r} rests on no sourced claim in {ANNOTATIONS}")
    seen = set()
    for tag in tag_map["tags"]:
        key = tag.get("key", "")
        if not re.fullmatch(r"[a-z0-9_]+", key) or key in seen:
            raise VisualError(f"map tag {tag} has no unique key")
        seen.add(key)
        if "status" in tag:
            raise VisualError(f"map tag {key!r} types a status; statuses are derived")
        on_flow, on_board = tag.get("flow") in tag_map["flows"], tag.get("board") in tag_map.get("boards", {})
        if on_flow == on_board:
            raise VisualError(f"map tag {key!r} must sit on exactly one flow or board in the map")
        if not tag.get("fields"):
            raise VisualError(f"map tag {key!r} names no field")
        for pair in tag["fields"]:
            registered = pair["field"] in registry.get(pair["source"], {}).get("fields", ())
            if pair.get("expect") == "unregistered" and registered:
                raise VisualError(f"map tag {key!r}: {pair_name(pair)} is now registered in {SOURCES}; "
                                  f"revisit the map and drop its expect: unregistered")
            if pair.get("expect") != "unregistered" and not registered:
                raise VisualError(f"map tag {key!r}: {pair_name(pair)} is not in {SOURCES}")


def model_pairs(declaration, derived):
    """The registry (source, field) pairs one model reads: its derived fields and its panel columns."""
    pairs = {tuple(f.split(".", 1)) for f in (derived or {}).get("fields", ())}
    for column in (declaration or {}).get("features", ()):
        pairs.update(FEATURE_FIELDS.get(column, ()))
    return pairs


def run_record_declarations(repo):
    """{relative path: {declaration, derived, comparison}} for each published record (top-level docs/runs/*.json).

    Only what a record declares is kept, and a comparison's verdict; no other
    result is read.
    """
    out = {}
    for path in sorted((Path(repo) / RUNS).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        kept = {k: record[k] for k in ("declaration", "derived") if k in record}
        if "comparison" in record:
            kept["comparison"] = {k: record["comparison"][k] for k in ("loss", "mean_difference_interval")
                                  if k in record["comparison"]}
        out[f"{RUNS}/{path.name}"] = kept
    return out


def is_published(rel):
    """A top-level JSON file in docs/runs/, not one under archive/."""
    return rel.startswith(RUNS + "/") and "/" not in rel[len(RUNS) + 1:] and rel.endswith(".json")


def published_uses(records):
    """[(record, pairs)] for each published single-model record."""
    out = []
    for rel, record in sorted(records.items()):
        declaration = record.get("declaration") or {}
        if is_published(rel) and "features" in declaration:
            out.append((rel, model_pairs(declaration, record.get("derived"))))
    return out


def hurt_verdicts(records):
    """[(record, added pairs, loss)] for each published comparison in which adding fields made the score worse.

    Only an ablation counts: the two models' declarations are the same except
    for their inputs, one reads every pair the other does and more, and the
    paired interval lies wholly on the side where the model with more inputs
    loses. The difference is loss(model_a) minus loss(model_b).
    """
    out = []
    for rel, record in sorted(records.items()):
        declaration, derived = record.get("declaration") or {}, record.get("derived") or {}
        interval = (record.get("comparison") or {}).get("mean_difference_interval")
        if not (is_published(rel) and interval and "model_a" in declaration and "model_b" in declaration):
            continue
        a, b = declaration["model_a"], declaration["model_b"]
        if {k: v for k, v in a.items() if k != "features"} != {k: v for k, v in b.items() if k != "features"}:
            continue
        pa = model_pairs(a, derived.get("model_a"))
        pb = model_pairs(b, derived.get("model_b"))
        loss = record["comparison"].get("loss", "score")
        if pb > pa and interval["upper"] < 0:
            out.append((rel, pb - pa, loss))
        elif pa > pb and interval["lower"] > 0:
            out.append((rel, pa - pb, loss))
    return out


def issue_index(snapshot, tag_map):
    """{number: entry} from the snapshot; a map issue the snapshot lacks is refused."""
    index = {e["number"]: e for e in snapshot["issues"]}
    for tag in tag_map["tags"]:
        missing = [n for n in tag["issues"] if n not in index]
        if missing:
            raise VisualError(f"map tag {tag['key']!r} names issues {missing} that {ISSUES} does not carry; "
                              f"run `python3 scripts/emit_visual.py --refresh-issues`")
    return index


def tag_statuses(tag_map, registry, manifest, records, snapshot, tracked):
    """Each tag's derived status, its reason and sub-line, and what its detail shows (#141 §3).

    The first matching rule wins: used, tried and hurt, in progress,
    registered but unused, not registered. `tracked` is the list of tracked
    files under tests/fixtures/snapshots/.
    """
    index = issue_index(snapshot, tag_map)
    uses = published_uses(records)
    verdicts = hurt_verdicts(records)
    publish = {}
    for e in snapshot["issues"]:
        m = PUBLISH_TITLE.match(e["title"])
        if m and e["state"] == "open":
            publish.setdefault(int(m.group(1)), []).append(e["number"])
    built, refused = set(manifest["built_columns"]), set(manifest["refused_columns"])
    rows = []
    for tag in tag_map["tags"]:
        pairs = {(p["source"], p["field"]) for p in tag["fields"]}
        names = ", ".join(f"<code>{s}.{f}</code>" for s, f in sorted(pairs))
        registered = all(f in registry.get(s, {}).get("fields", ()) for s, f in pairs)
        status = reason = sub = None
        user = next((rel for rel, used in uses if pairs <= used), None)
        hurt = next(((rel, loss) for rel, added, loss in verdicts if pairs <= added), None)
        working = [(n, index[n]) for n in tag["issues"] if index[n]["state"] == "open"
                   and ("in-progress" in index[n]["labels"] or index[n]["open_prs"])]
        asking = [(n, q) for n in tag["issues"] if index[n]["state"] == "closed" for q in publish.get(n, ())]
        queued = [n for n in tag["issues"] if index[n]["state"] == "open" and "directive" in index[n]["labels"]
                  and (n, index[n]) not in working]
        if registered and user:
            status, reason = "used", f"in the published declaration <code>{user}</code>"
        elif registered and hurt:
            status, reason = "tried_and_hurt", (f"adding it made the paired {hurt[1].replace('_', ' ')} worse in "
                                                f"<code>{hurt[0]}</code>")
        elif working:
            n, e = working[0]
            status = "in_progress"
            reason = (f"open pull request #{e['open_prs'][0]} for #{n}" if e["open_prs"]
                      else f"#{n} is being worked on")
        elif registered and asking:
            n, q = asking[0]
            status, reason = "in_progress", f"directive #{n} is done, and its publishing question #{q} is open"
        elif registered:
            status, reason = "registered_unused", "registered, and no published declaration reads it"
            sub = ("queued: " + ", ".join(f"#{n}" for n in queued)) if queued else None
        else:
            status, reason = "not_registered", f"no source in <code>{SOURCES}</code> carries it"
        columns = sorted({c for c, fields in FEATURE_FIELDS.items() if pairs & set(fields)})
        panel = ([f"<code>{c}</code>" + ("" if c in built else ", refused by the panel" if c in refused
                                         else ", not built") for c in columns] or ["not in the panel"])
        where = tag.get("fixtures")
        data_in_repo = bool(where) and any(
            f.startswith(where.rstrip("/") + "/") and f.endswith(".manifest.json") for f in tracked)
        rows.append({"key": tag["key"], "label": tag["label"], "flow": tag.get("flow"), "board": tag.get("board"),
                     "status": status,
                     "reason": reason, "sub": sub, "fields": names, "panel": "; ".join(panel),
                     "data_in_repo": data_in_repo, "issues": list(tag["issues"])})
    return rows


def where_label(row, tag_map, parties):
    """Where a tag sits: "From &rarr; To" for a flow, the board's label for a board."""
    if row.get("flow"):
        flow = tag_map["flows"][row["flow"]]
        return f'{parties[flow["from"]]} &rarr; {parties[flow["to"]]}'
    return html.escape(tag_map["boards"][row["board"]]["label"])


def status_table(rows, tag_map, parties):
    """The generated status table for N4's "Go deeper" fold."""
    marks = {key: (icon, word_) for key, icon, word_ in STATUSES}
    body = []
    for r in rows:
        icon, word_ = marks[r["status"]]
        sub = f'<small>{html.escape(r["sub"])}</small>' if r["sub"] else ""
        body.append(
            f'<tr id="tag-{r["key"]}"><th scope="row">{html.escape(r["label"])}</th>'
            f'<td data-h="Flow">{where_label(r, tag_map, parties)}</td>'
            f'<td data-h="Status"><span class="status s-{r["status"]}"><span aria-hidden="true">{icon}</span> '
            f'{word_}</span><small>{r["reason"]}</small>{sub}</td>'
            f'<td data-h="Registry">{r["fields"]}</td><td data-h="Panel">{r["panel"]}</td>'
            f'<td data-h="Data in this repository">{"yes" if r["data_in_repo"] else "no"}</td></tr>')
    return ('<table class="tags"><thead><tr><th scope="col">Tag</th><th scope="col">Flow</th>'
            '<th scope="col">Status</th><th scope="col">Registry</th><th scope="col">Panel</th>'
            '<th scope="col">Data in this repository</th></tr></thead><tbody>' + "".join(body) + "</tbody></table>")


def check_map_text(tag_map, notes, glossary):
    """Refuse a map whose drawing or wording it cannot back.

    Every party has a place on the map, every flow a known kind, and every
    tag's plain description (`about`) is a glossary term or a sourced claim in
    `annotations.json`. A tag with no `about` is described by its registry
    entry alone.
    """
    terms = {t["key"] for t in glossary["terms"]}
    kinds = {k for k, _, _ in FLOW_KINDS}
    for key in tag_map["parties"]:
        point = tag_map["layout"].get(key)
        if not (isinstance(point, list) and len(point) == 2):
            raise VisualError(f"map party {key!r} has no place in the map's layout")
    for key, flow in tag_map["flows"].items():
        if flow["kind"] not in kinds:
            raise VisualError(f"map flow {key!r} is of kind {flow['kind']!r}, which the map does not draw")
        for end in (flow["from"], flow["to"]):
            if end not in tag_map["parties"]:
                raise VisualError(f"map flow {key!r} names a party {end!r} the map does not list")
    for key in tag_map.get("boards", {}):
        if key not in tag_map["parties"]:
            raise VisualError(f"map board {key!r} sits under no party the map lists")
    for tag in tag_map["tags"]:
        about = tag.get("about")
        if about is None:
            continue
        if "term" in about and about["term"] not in terms:
            raise VisualError(f"map tag {tag['key']!r} is described by glossary term {about['term']!r}, "
                              f"which {GLOSSARY} does not define")
        if "claim" in about and about["claim"] not in notes["claims"]:
            raise VisualError(f"map tag {tag['key']!r} is described by claim {about['claim']!r}, "
                              f"which {ANNOTATIONS} does not carry")
        if set(about) not in ({"term"}, {"claim"}):
            raise VisualError(f"map tag {tag['key']!r}: about names one glossary term or one claim")


def segment_days(rows, locked, on_rrp, registry, decision):
    """The days N4's segment chart draws, chosen by `SEGMENT_DAY_RULE` from inputs known in advance.

    Reads only `SEGMENT_RULE_COLUMNS` of each row and the ON RRP results, never
    a rate. A quarter-end's ON RRP reading is the one public at its decision
    instant: the declared decision time on the panel day before it. Days in a
    locked tier are never chosen. Returns `[{"date", "why", "on_rrp"}]` in date
    order, `why` naming each clause the day meets.
    """
    before = SEGMENT_DAY_RULE["before"]
    deadlines = {corporate_tax_deadline(y, m).isoformat()
                 for y in {int(r["date"][:4]) for r in rows} for m in TAX_DEADLINE_MONTHS}
    out = []
    for i, r in enumerate(rows):
        today = date.fromisoformat(r["date"])
        if r["date"] >= before or locked_tier(today, locked) is not None:
            continue
        why, reading = [], None
        if r["quarter_end"] == "1" and i > 0:
            ref, value = on_rrp_as_of(on_rrp, date.fromisoformat(rows[i - 1]["date"]), decision, registry)
            reading = {"ref": ref.isoformat(), "bn": round(float(value), 3)}
            if value < SEGMENT_DAY_RULE["on_rrp_below_bn"]:
                why.append("quarter_end")
        if r["date"] in deadlines and float(r["treasury_settlement_coupons"] or 0) > 0:
            why.append("tax_coupon")
        if why:
            out.append({"date": r["date"], "why": why, "on_rrp": reading if "quarter_end" in why else None})
    return out


def segment_spreads(rows, chosen):
    """Each chosen day's TGCR, BGCR and SOFR less IORB, in whole basis points (`Decimal`)."""
    by_date = {r["date"]: r for r in rows}
    out = []
    for d in chosen:
        r = by_date[d["date"]]
        iorb = Decimal(r["iorb"])
        out.append(dict(d, **{k: int((Decimal(r[k]) - iorb) * 100) for k, _ in SEGMENTS}))
    return out


def wrap(text, width):
    lines = []
    for w in text.split():
        if lines and len(lines[-1]) + 1 + len(w) <= width:
            lines[-1] += " " + w
        else:
            lines.append(w)
    return lines


def map_svg(tag_map, rows, parties, prefix="n4"):
    """N4's map as a static, accessible <svg>: parties, one arrow per flow, the board under the dealers.

    Each arrow points the way the cash goes and is drawn in its kind's line
    style. An arrow no registered series on the map measures is drawn faint;
    that is derived from the tags' statuses, never typed. Each arrow carries
    its flow's number from the list beside the map. `prefix` keeps the ids of
    N5's copy apart from N4's.
    """
    hw, layout = 88, tag_map["layout"]
    dash = {k: d for k, _, d in FLOW_KINDS}
    label = {k: lab for k, lab, _ in FLOW_KINDS}
    measured = {r["flow"] for r in rows if r["flow"] and r["status"] != "not_registered"}
    boxes = {}
    for key, name in tag_map["parties"].items():
        lines = wrap(html.unescape(name), 24)
        boxes[key] = (layout[key][0], layout[key][1], hw, 12 + 8 * len(lines), lines)

    def edge(key, toward):
        x, y, w, h, _ = boxes[key]
        dx, dy = toward[0] - x, toward[1] - y
        t = min(w / abs(dx) if dx else math.inf, h / abs(dy) if dy else math.inf)
        n = math.hypot(dx, dy)
        return x + dx * t + 5 * dx / n, y + dy * t + 5 * dy / n

    parts, names = [], []
    for n, (key, flow) in enumerate(tag_map["flows"].items(), 1):
        a, b = layout[flow["from"]], layout[flow["to"]]
        bend = flow.get("bend", 0)
        if bend:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            px, py = (b[1] - a[1]) / length, -(b[0] - a[0]) / length
            c = ((a[0] + b[0]) / 2 + bend * px, (a[1] + b[1]) / 2 + bend * py)
            (x1, y1), (x2, y2) = edge(flow["from"], c), edge(flow["to"], c)
            d = f"M{x1:.1f},{y1:.1f} Q{c[0]:.1f},{c[1]:.1f} {x2:.1f},{y2:.1f}"
            mx, my = 0.25 * x1 + 0.5 * c[0] + 0.25 * x2, 0.25 * y1 + 0.5 * c[1] + 0.25 * y2
        else:
            (x1, y1), (x2, y2) = edge(flow["from"], b), edge(flow["to"], a)
            d = f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        faint = key not in measured
        style = f"stroke:var({'--ink-3' if faint else '--ink-2'})" + (f";stroke-dasharray:{dash[flow['kind']]}"
                                                                      if dash[flow["kind"]] else "")
        parts.append(
            f'<g class="fl{" faint" if faint else ""}" id="{prefix}f-{key}"><path d="{d}" style="{style}" '
            f'marker-end="url(#{prefix}-head)"/><circle cx="{mx:.1f}" cy="{my:.1f}" r="11"/>'
            f'<text x="{mx:.1f}" y="{my + 4:.1f}" text-anchor="middle">{n}</text></g>')
        names.append(f"{n}, {html.unescape(parties[flow['from']])} to {html.unescape(parties[flow['to']])}: "
                     f"{label[flow['kind']].split(':')[0].lower()}"
                     + (", measured by no registered series on this map" if faint else ""))
    for key, (x, y, w, h, lines) in boxes.items():
        text = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else 15}">{html.escape(t)}</tspan>'
                       for i, t in enumerate(lines))
        parts.append(f'<g class="party"><rect x="{x - w}" y="{y - h}" width="{2 * w}" height="{2 * h}" rx="8"/>'
                     f'<text x="{x}" y="{y + 4 - 7.5 * (len(lines) - 1):.1f}" text-anchor="middle">{text}</text></g>')
    for key, board in tag_map.get("boards", {}).items():
        x, y, w, h, _ = boxes[key]
        top = y + h + 44
        parts.append(f'<g class="board" id="{prefix}b-{key}"><line x1="{x}" y1="{y + h}" x2="{x}" y2="{top}"/>'
                     f'<rect x="{x - w}" y="{top}" width="{2 * w}" height="34" rx="8"/>'
                     f'<text x="{x}" y="{top + 21}" text-anchor="middle">{html.escape(board["label"])}</text></g>')
        names.append(f"a board of market-wide series under {html.unescape(parties[key])}")
    aria = ("Map of who lends cash to whom. Each arrow points the way the cash goes. "
            + "; ".join(names) + ". The list below the map gives the same flows and their tags.")
    return (f'<svg viewBox="-20 0 800 480" role="img" aria-label="{html.escape(aria)}">'
            f'<defs><marker id="{prefix}-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="12" markerHeight="12" markerUnits="userSpaceOnUse" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--ink-2)"/></marker></defs>'
            + "".join(parts) + "</svg>")


def chip(r):
    icon, word_ = {k: (i, w) for k, i, w in STATUSES}[r["status"]]
    return (f'<button type="button" class="chip" data-flow="{r["flow"] or ""}" data-board="{r["board"] or ""}" '
            f'aria-pressed="false" aria-expanded="false" aria-controls="n4d-{r["key"]}">'
            f'<span aria-hidden="true">{icon}</span> {html.escape(r["label"])} <small>{word_}</small></button>')


def flow_list(tag_map, rows, parties, notes):
    """The flows in order, each with its sourced claim and its tags as buttons; the boards after them.

    This is the map's keyboard and phone form: the same flows and tags, in
    flow order.
    """
    label = {k: lab for k, lab, _ in FLOW_KINDS}
    items = []
    for n, (key, flow) in enumerate(tag_map["flows"].items(), 1):
        mine = [r for r in rows if r["flow"] == key]
        claim = notes["claims"][flow["claim"]]
        none = ("" if any(r["status"] != "not_registered" for r in mine) else
                "<small class='none'>No registered series on this map measures this flow.</small>")
        items.append(
            f'<li id="n4l-{key}"><span class="fn" aria-hidden="true">{n}</span><div><b>{parties[flow["from"]]} '
            f'&rarr; {parties[flow["to"]]}</b><small>{label[flow["kind"]]}. {link(claim)}</small>{none}'
            f'<div class="chips">{"".join(chip(r) for r in mine)}</div></div></li>')
    for key, board in tag_map.get("boards", {}).items():
        mine = [r for r in rows if r["board"] == key]
        items.append(
            f'<li id="n4l-board-{key}"><span class="fn" aria-hidden="true">&#9638;</span><div>'
            f'<b>{html.escape(board["label"])}</b><small>{link(notes["claims"][board["claim"]])}</small>'
            f'<div class="chips">{"".join(chip(r) for r in mine)}</div></div></li>')
    return f'<ol class="n4list" aria-label="Flows of cash and the series that measure them">{"".join(items)}</ol>'


def tag_details(tag_map, rows, registry, notes, glossary, parties):
    """One hidden detail panel per tag, opened by its button: status and reason, description, registry, panel, data."""
    terms = {t["key"]: t for t in glossary["terms"]}
    marks = {k: (i, w) for k, i, w in STATUSES}
    label = {k: lab for k, lab, _ in FLOW_KINDS}
    tags = {t["key"]: t for t in tag_map["tags"]}
    out = []
    for r in rows:
        tag, (icon, word_) = tags[r["key"]], marks[r["status"]]
        about = tag.get("about") or {}
        if "term" in about:
            t = terms[about["term"]]
            text = f'<p><b>{html.escape(t["term"])}:</b> {html.escape(t["definition"])} <a href="{t["src"]}">Source</a></p>'
        elif "claim" in about:
            text = f"<p>{link(notes['claims'][about['claim']])}</p>"
        else:
            text = ""
        sources = []
        for source in dict.fromkeys(p["source"] for p in tag["fields"]):
            entry = registry.get(source)
            if entry is None:
                sources.append(f"<code>{source}</code>: not in the registry")
                continue
            fields = [p["field"] for p in tag["fields"] if p["source"] == source]
            freq = sorted({(entry.get("field_frequencies") or {}).get(f, entry["frequency"]).replace("_", " ")
                           for f in fields})
            sources.append(f'<a href="{entry["url"]}">{html.escape(entry["provider"])}</a>, '
                           f'{" and ".join(freq)}: {"; ".join(html.escape(c) for c in entry["coverage"])}')
        where = (f'{where_label(r, tag_map, parties)}, {label[tag_map["flows"][r["flow"]]["kind"]].split(":")[0].lower()}'
                 if r["flow"] else where_label(r, tag_map, parties))
        issues = ", ".join(f'<a href="https://github.com/{REPOSITORY}/issues/{n}">#{n}</a>' for n in r["issues"])
        sub = f" {html.escape(r['sub'])}." if r["sub"] else ""
        out.append(
            f'<div class="n4d" id="n4d-{r["key"]}" role="region" aria-labelledby="n4d-{r["key"]}-h" hidden>'
            f'<h3 id="n4d-{r["key"]}-h">{html.escape(r["label"])}</h3>'
            f'<p class="st"><span class="status"><span aria-hidden="true">{icon}</span> {word_}</span>: '
            f'{r["reason"]}.{sub}</p>{text}<dl>'
            f'<dt>Where</dt><dd>{where}</dd>'
            f'<dt>Registry</dt><dd>{r["fields"]}<br>{"<br>".join(sources)}</dd>'
            f'<dt>Panel</dt><dd>{r["panel"]}</dd>'
            f'<dt>Data in this repository</dt><dd>{"yes" if r["data_in_repo"] else "no"}</dd>'
            + (f"<dt>Issues</dt><dd>{issues}</dd>" if issues else "")
            + '</dl><button type="button" class="n4close">Close</button></div>')
    return "".join(out)


def segment_held_note(locked):
    """The segment chart's held-out sentence, from the lockbox and the rule's own cut-off."""
    before = date.fromisoformat(SEGMENT_DAY_RULE["before"])
    starts = sorted(t.start for t in locked)
    if starts and starts[0] < before:
        return (f"Days from {day(starts[0].isoformat())} on are {held_as(t.name for t in locked)}, "
                f"and are never chosen.")
    first = min(locked, key=lambda t: t.start) if locked else None
    lock = (f"; the {first.name.replace('_', '-')} tier, which no test has opened, starts on "
            f"{day(first.start.isoformat())}" if first else "")
    return f"No day in this chart is held out: the rule picks only days before {day(before.isoformat())}{lock}."


def segment_table(days):
    """The segment chart's values as a table, for the "Go deeper" fold."""
    why = {"quarter_end": "Quarter-end, ON RRP low", "tax_coupon": "Tax date on a coupon settlement"}
    body = "".join(
        f'<tr><th scope="row">{short_day(d["date"])}</th><td>{" and ".join(why[w] for w in d["why"])}</td>'
        + "".join(f"<td>{bp(d[k])}</td>" for k, _ in SEGMENTS) + "</tr>" for d in days)
    head = "".join(f'<th scope="col">{name} − IORB, bp</th>' for _, name in SEGMENTS)
    return (f'<div class="heat" role="region" aria-label="Table of the segment rates on the chosen days" tabindex="0">'
            f'<table class="segtab"><thead><tr><th scope="col">Day</th><th scope="col">Chosen because</th>{head}'
            f'</tr></thead><tbody>{body}</tbody></table></div>')


def newcomer_n4(tag_map, registry, manifest, records, snapshot, tracked, notes, glossary, seg_rows, seg_days,
                decision, locked):
    """N4 "Who lends to whom": the map, its tags and their derived statuses, and the segment chart (#144, #145)."""
    check_map(tag_map, registry, notes)
    check_map_text(tag_map, notes, glossary)
    rows = tag_statuses(tag_map, registry, manifest, records, snapshot, tracked)
    parties = {k: html.escape(v) for k, v in tag_map["parties"].items()}
    used = sum(1 for r in rows if r["status"] == "used")
    retrieved = snapshot["retrieved_at"]
    days = segment_spreads(seg_rows, seg_days)
    if not days:
        raise VisualError("the segment-day rule chose no day; N4's segment chart has nothing to draw")
    kinds = {r: sum(1 for d in days if r in d["why"]) for r in ("quarter_end", "tax_coupon")}
    before = SEGMENT_DAY_RULE["before"]
    below = f"${SEGMENT_DAY_RULE['on_rrp_below_bn']:,.0f}bn"
    data = {"tags": rows, "issues_retrieved_at": retrieved,
            "statuses": [{"key": k, "icon": i, "word": w} for k, i, w in STATUSES],
            "segments": {"days": days, "rule": dict(SEGMENT_DAY_RULE), "rule_columns": list(SEGMENT_RULE_COLUMNS),
                         "series": [{"key": k, "label": name} for k, name in SEGMENTS],
                         "on_rrp": {"source": NYFED_ON_RRP_SOURCE_ID, "field": NYFED_ON_RRP_FIELD}}}
    fills = {
        "n4_lede": (f"Of the {word(len(rows))} public series on this market's map, {word(used)} "
                    f"{'is' if used == 1 else 'are'} read by a published forecast. Each tag on the map says "
                    f"which, and why or why not; it is worked out from the repository, not typed."),
        "n4_status_table": status_table(rows, tag_map, parties),
        "n4_retrieved": f"{day(retrieved[:10])} ({retrieved[11:16]} UTC)",
        "n4_map": map_svg(tag_map, rows, parties),
        "n4_list": flow_list(tag_map, rows, parties, notes),
        "n4_details": tag_details(tag_map, rows, registry, notes, glossary, parties),
        "n4_kinds": "".join(
            f'<li><svg viewBox="0 0 40 10" aria-hidden="true"><line x1="0" y1="5" x2="40" y2="5" '
            f'style="stroke:var(--ink-2){";stroke-dasharray:" + d if d else ""}"/></svg>{html.escape(lab)}</li>'
            for _, lab, d in FLOW_KINDS),
        "n4_seg_rule": (f"every quarter-end before {day(before)} on which the ON RRP result public at the "
                        f"{clock(decision)} decision the business day before was below {below}, and every corporate "
                        f"tax deadline before then on which Treasury coupon securities settled"),
        "n4_seg_counts": (f"{word(len(days)).capitalize()} days: {word(kinds['quarter_end'])} "
                          f"{'quarter-end' if kinds['quarter_end'] == 1 else 'quarter-ends'} and "
                          f"{word(kinds['tax_coupon'])} tax {'deadline' if kinds['tax_coupon'] == 1 else 'deadlines'}"
                          + (", one day meeting both" if len(days) < sum(kinds.values()) else "")),
        "n4_seg_table": segment_table(days),
        "n4_seg_held": segment_held_note(locked),
        "c_segments_none": link(notes["claims"]["segments_none"]),
        "c_fhlb_fed_funds": link(notes["claims"]["fhlb_fed_funds"]),
    }
    return data, fills


def tracked_snapshots(repo):
    out = git(repo, "ls-files", "--", SNAPSHOTS)
    return tuple(out.splitlines()) if out else ()


def gh_fetch(path):
    """One REST call through the `gh` CLI. Used only by `--refresh-issues`."""
    done = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if done.returncode:
        raise VisualError(f"gh api {path}: {done.stderr.strip()[-300:]}")
    return json.loads(done.stdout)


def refresh_issues(tag_map, fetch, now):
    """The bytes of `docs/visual/issues.json`: the map's issues, their "Publish?" questions, and open pull requests.

    Reads the repository's issue list page by page through `fetch` (REST; pull
    requests come in the same list). Keeps each issue the map names, each open
    or closed "Publish? … (#N)" issue for such an N, and for each kept issue the
    open pull requests whose body says "Closes #N".
    """
    wanted = sorted({n for tag in tag_map["tags"] for n in tag["issues"]})
    listing, page = [], 1
    while True:
        batch = fetch(f"repos/{REPOSITORY}/issues?state=all&per_page=100&page={page}")
        if not batch:
            break
        listing.extend(batch)
        page += 1
    issues = {e["number"]: e for e in listing if "pull_request" not in e}
    missing = [n for n in wanted if n not in issues]
    if missing:
        raise VisualError(f"the map names issues {missing} that {REPOSITORY} does not have")
    keep = set(wanted)
    for e in issues.values():
        m = PUBLISH_TITLE.match(e["title"])
        if m and int(m.group(1)) in keep:
            keep.add(e["number"])
    open_prs = {}
    for e in listing:
        if "pull_request" in e and e["state"] == "open":
            for n in re.findall(r"(?i)\bcloses #(\d+)\b", e.get("body") or ""):
                open_prs.setdefault(int(n), []).append(e["number"])
    doc = {"repository": REPOSITORY, "retrieved_at": now, "issues": [
        {"number": n, "title": issues[n]["title"], "state": issues[n]["state"],
         "labels": sorted(label["name"] for label in issues[n]["labels"]), "open_prs": sorted(open_prs.get(n, []))}
        for n in sorted(keep)]}
    return (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


# ---------------------------------------------------------------- N3 "When does it happen?" (#147)


def snapshot_series(repo, root, series_id):
    """One series from the tracked snapshots under `root`, through `ingest`'s own adapter.

    `parse_snapshots` refuses a file whose bytes do not match its manifest's
    SHA-256. A day's value is the latest vintage of it. Returns
    `([(ref_date, available_at, value)], {snapshot path: sha256})`, the values
    ordered by when they became public.
    """
    manifests = sorted((repo / root).glob("*.json.manifest.json"))
    if not manifests:
        raise VisualError(f"no snapshot under {root}")
    artifacts = [load_snapshot_manifest(path) for path in manifests]
    latest = {}
    for row in parse_snapshots(artifacts).rows:
        if row.series_id != series_id:
            continue
        if row.ref_date not in latest or row.available_at > latest[row.ref_date][0]:
            latest[row.ref_date] = (row.available_at, row.value)
    results = sorted(((ref, at, value) for ref, (at, value) in latest.items()), key=lambda o: (o[1], o[0]))
    snapshots = {}
    for path in manifests:
        payload = path.with_name(path.name[:-len(".manifest.json")])
        snapshots[str(payload.relative_to(repo))] = sha256(payload)
    return results, snapshots


def on_rrp_results(repo):
    """The Desk's ON RRP results (USD billions), from the tracked snapshots: `snapshot_series` on `ON_RRP`."""
    return snapshot_series(repo, ON_RRP, NYFED_ON_RRP_FIELD)


def on_rrp_as_of(results, day, decision, registry):
    """`(ref_date, value)`: the latest ON RRP result public at the decision instant of `day`.

    `results` is `on_rrp_results(...)[0]`, ordered by availability. The
    availability is the adapter's, from the registry's declaration (16:00 ET on
    the next business day), so a 16:00 reading on `day` sees the previous
    business day's operation. A reading older than the declaration's
    `worst_case_calendar_days` is refused (`ValueError`), never carried.
    """
    lag = registry[NYFED_ON_RRP_SOURCE_ID]["release_lag"]
    instant = datetime.combine(day, decision, ZoneInfo(lag["timezone"]))
    times = [at for _, at, _ in results]
    position = bisect.bisect_right(times, instant) - 1
    if position < 0:
        raise ValueError(f"no ON RRP result was public at {instant.isoformat()}")
    ref, _, value = results[position]
    limit = int(lag["worst_case_calendar_days"])
    if (day - ref).days > limit:
        raise ValueError(f"the ON RRP reading on {day.isoformat()} is from {ref.isoformat()}, more than "
                         f"{limit} calendar days old; refusing rather than carrying it")
    return ref, value


def rate_cell(outcomes):
    """k, n, the share, and its stationary-bootstrap interval, as `scarcity.tabulate` reports a frequency."""
    n, k = len(outcomes), sum(outcomes)
    if not n:
        return {"k": 0, "rate": None, "interval": None}
    lo, hi = stationary_bootstrap_interval(
        lambda indices: sum(outcomes[i] for i in indices) / len(indices), n,
        block_length=min(BOOTSTRAP_BLOCK_LENGTH, n), seed=BOOTSTRAP_SEED,
        replications=BOOTSTRAP_REPLICATIONS, level=BOOTSTRAP_LEVEL)
    return {"k": k, "rate": k / n, "interval": [lo, hi]}


def pct(x):
    """A share in percent: one decimal below 10%, so a small cell does not read as zero."""
    return f"{100 * x:.1f}%" if 0 < x < 0.1 else f"{round(100 * x)}%"


def newcomer_n3(rows, locked, thresholds, registry, decision, on_rrp, notes):
    """N3 "When does it happen?": the 2x2 of quarter-end against scarce or abundant cash (#147).

    Each counted day falls in one cell: inside a quarter-end window or not
    (`data.quarter_end_window`, #140), and with the ON RRP reading public at the
    decision instant below `contract.ON_RRP_DEPLETION_BREAK_BN` (scarce) or not
    (abundant). Each cell reports the share of its days with SOFR - IORB, on
    whole basis points, strictly above each headline threshold: k of n, with an
    interval. The #115 scarcity state is not read here: it is the band
    (`newcomer_band`), and the 2x2 keeps the ON RRP break alone. Days in a
    locked tier are left out of every cell, count and sentence
    (`counted`), and the view says so.
    """
    taus = [int(t) for t in thresholds["taus_bp"]]
    pressure_bp, second_bp = taus[0], taus[1]
    kept = counted(rows, locked)
    if not kept:
        raise VisualError("every panel day is held out; N3 has nothing to count")
    groups = {(scarce, qe): [] for scarce in (True, False) for qe in (True, False)}
    for r in kept:
        today = date.fromisoformat(r["date"])
        _, value = on_rrp_as_of(on_rrp, today, decision, registry)
        spread = int((Decimal(r["sofr"]) - Decimal(r["iorb"])) * 100)
        groups[(value < ON_RRP_DEPLETION_BREAK_BN, quarter_end_window(today) == 1.0)].append(spread)
    cells = [{"scarce": scarce, "quarter_end": qe, "n": len(spreads),
              "above": {str(tau): rate_cell([int(s > tau) for s in spreads]) for tau in (pressure_bp, second_bp)}}
             for (scarce, qe), spreads in groups.items()]
    cell = {(c["scarce"], c["quarter_end"]): c for c in cells}
    spans = held_out_spans(rows, locked)
    lag = registry[NYFED_ON_RRP_SOURCE_ID]["release_lag"]
    brk = f"${ON_RRP_DEPLETION_BREAK_BN:,.0f}bn"

    def kn(c, tau):
        return f"{c['above'][str(tau)]['k']} of {c['n']}"

    def table(tau):
        head = "<tr><th></th><th scope='col'>Quarter-end window</th><th scope='col'>Other days</th></tr>"
        body = []
        for scarce, name in ((True, f"Scarce cash: ON RRP below {brk}"), (False, f"Abundant cash: ON RRP at or above {brk}")):
            tds = []
            for qe in (True, False):
                c = cell[(scarce, qe)]
                a = c["above"][str(tau)]
                if not c["n"]:
                    tds.append("<td>no days</td>")
                    continue
                lo, hi = a["interval"]
                tds.append(f"<td style='--share:{round(100 * a['rate'])}%'><b>{pct(a['rate'])}</b>"
                           f"<span>{a['k']} of {c['n']} days</span><small>{round(100 * BOOTSTRAP_LEVEL)}% interval "
                           f"{pct(lo)} to {pct(hi)}</small></td>")
            body.append(f"<tr><th scope='row'>{name}</th>{''.join(tds)}</tr>")
        if spans:
            held = " and ".join(f"{day(h['start'])} to {day(h['end'])}" for h in spans)
            body.append(f"<tr><td colspan='3' class='held'>Held out, not in any cell: {held}</td></tr>")
        return (f"<table><caption>Share of days with SOFR more than +{tau} bp above IORB</caption>"
                f"<thead>{head}</thead><tbody>{''.join(body)}</tbody></table>")

    sq, so = cell[(True, True)], cell[(True, False)]
    aq, ao = cell[(False, True)], cell[(False, False)]
    window_days = 2 * QUARTER_END_WINDOW_BUSINESS_DAYS + 1
    data = {
        "column": "quarter_end_window", "window_business_days": QUARTER_END_WINDOW_BUSINESS_DAYS,
        "pressure_bp": pressure_bp, "second_bp": second_bp, "break_bn": ON_RRP_DEPLETION_BREAK_BN,
        "cells": cells, "held_out": spans,
        "counted": {"first": kept[0]["date"], "last": kept[-1]["date"], "n": len(kept)},
        "on_rrp": {"source": NYFED_ON_RRP_SOURCE_ID, "field": NYFED_ON_RRP_FIELD,
                   "release_lag": {k: lag[k] for k in ("days", "unit", "available_time", "timezone")}},
        "bootstrap": {"method": "stationary", "block_length": BOOTSTRAP_BLOCK_LENGTH, "level": BOOTSTRAP_LEVEL,
                      "replications": BOOTSTRAP_REPLICATIONS, "seed": BOOTSTRAP_SEED},
    }
    fills = {
        "n3_lede": (f"With cash scarce, SOFR closed more than +{pressure_bp} bp above IORB on {kn(sq, pressure_bp)} "
                    f"days in a quarter-end window and {kn(so, pressure_bp)} other days counted here; with cash "
                    f"abundant, on {kn(aq, pressure_bp)} quarter-end window days and {kn(ao, pressure_bp)} other days."),
        "n3_table": table(pressure_bp), "n3_table_second": table(second_bp),
        "n3_first": day(kept[0]["date"]), "n3_last": day(kept[-1]["date"]),
        "n3_break": brk,
        "n3_window_caption": (
            f"Quarter-end here is the column <code>quarter_end_window</code>: the quarter's last business day and "
            f"the {word(QUARTER_END_WINDOW_BUSINESS_DAYS)} business days either side, {word(window_days)} days in "
            f"all (<a href='https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/decisions/"
            f"quarter-end-window.md'>the decision</a>). A one-day flag on the last business day alone would put "
            f"pressure on the days around it in &ldquo;other days&rdquo;."),
        "n3_read": (f"Each day is classed by the ON RRP result public at {clock(decision)} New York time that day. "
                    f"The project dates a result to {lag['available_time']} on the next business day, because the "
                    f"New York Fed states no publication time, so the reading is the previous business day's "
                    f"operation."),
        "n3_small": (f"The quarter-end cells are small, {days(sq['n'])} with scarce cash and {days(aq['n'])} with "
                     f"abundant cash, so their intervals are wide."),
        "n3_reading": (
            ("With cash scarce, pressure also came on days outside the quarter-end window. " if so["above"][str(pressure_bp)]["k"]
             else "With cash scarce, no day outside the quarter-end window saw pressure. ")
            + ("With cash abundant, quarter-ends did not always pass quietly." if aq["above"][str(pressure_bp)]["k"]
               else "With cash abundant, every quarter-end window counted here passed quietly.")),
        "n3_held_note": (f"Days from {day(spans[0]['start'])} on are {held_as(h['name'] for h in spans)}. "
                         f"They are in no cell and no sentence "
                         f"in this view." if spans else "No day in this view is held out."),
        "n3_interval": (f"Each interval is a {round(100 * BOOTSTRAP_LEVEL)}% stationary-bootstrap interval that "
                        f"resamples a cell's days in blocks averaging {BOOTSTRAP_BLOCK_LENGTH} days, because "
                        f"pressure days come in runs."),
        "c_n3_quarter_end": link(notes["claims"]["quarter_end"]),
        "c_n3_fed_cash": link(notes["claims"]["fed_cash"]),
    }
    return data, fills


# ---------------------------------------------------------------- the reserve-scarcity band behind N1 and N3 (#148)

#: The map tag whose derived status the band's legend shows (#141 §4, N3's status logic).
BAND_TAG = "scarcity"


def snapshot_digests(repo, *roots):
    """{path: sha256} for every tracked payload under `roots`, manifests aside."""
    return {str(p.relative_to(repo)): sha256(p) for root in roots for p in sorted((repo / root).rglob("*"))
            if p.is_file() and not p.name.endswith(".manifest.json")}


def scarcity_days(repo, locked):
    """Every scored day before the first locked one, with the #115 state read as-of at its decision instant.

    The measurement panel is `scripts/scarcity_validation.py`'s, built from the
    tracked fixtures (funding inputs, the Desk's ON RRP results, the H.8 first
    prints) and refused unless its published columns reproduce the published
    digest. The state is `scarcity.with_reserve_scarcity_state`'s, read on the
    published scored grid by `scarcity.pressure_days_by_state` -- the reads
    #115 validated, through both read guards. `end` is the panel's last day in
    no locked tier, so the lockbox's own guard is never asked to score one.
    Returns `(scored days, {snapshot path: sha256})`.
    """
    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _, registry, decision = build_measurement_panel(repo / SOURCES, Path(tmp))
        rows = with_reserve_scarcity_state(build.observations)
        open_days = [r.date for r in rows if locked_tier(r.date, locked) is None]
        if not open_days:
            raise VisualError("every panel day is held out; the band has nothing to read")
        scored = pressure_days_by_state(rows, registry=registry, decision_time=decision,
                                        minimum_history=N2_MINIMUM_HISTORY, end=open_days[-1])
    return scored, snapshot_digests(repo, ON_RRP, H8)


def runs(days, key):
    """`[[first, last, value]]`: maximal runs of consecutive days with the same `key(day)`."""
    out = []
    for d in days:
        value = key(d)
        if out and out[-1][2] == value:
            out[-1][1] = d.day.isoformat()
        else:
            out.append([d.day.isoformat(), d.day.isoformat(), value])
    return out


def newcomer_band(scored, locked, thresholds, registry, decision, on_rrp, status, notes):
    """The #115 reserve-scarcity state as a band lane, with the ON RRP buffer as its sub-lane (#148).

    `scored` is `scarcity_days(...)[0]`: each scored day's as-of state and its
    own SOFR - IORB. A day in a locked tier is dropped here, whatever it holds,
    and is in no span, count or sentence. The sub-lane marks the days N3's 2x2
    calls scarce: the ON RRP result public at the decision instant below
    `contract.ON_RRP_DEPLETION_BREAK_BN`. Per state, the share of days strictly
    above each headline threshold on whole basis points, k of n with an
    interval, exactly as `scarcity.tabulate` reports it for #115. The caption
    says from those shares whether pressure-day frequency rises with the state;
    when it does not, it says so plainly and that the band is not a working
    indicator (Eleonora's ruling of 2 October 2026 on #148). `status` is the
    N4 engine's derived status for the map tag `BAND_TAG`.
    """
    taus = [int(t) for t in thresholds["taus_bp"][:2]]
    kept = [d for d in scored if locked_tier(d.day, locked) is None]
    if not kept:
        raise VisualError("every scored day is held out; the band has nothing to draw")
    spans = runs(kept, lambda d: None if d.state is None else int(d.state))

    def scarce(d):
        return on_rrp_as_of(on_rrp, d.day, decision, registry)[1] < ON_RRP_DEPLETION_BREAK_BN

    buffer_spans = [[a, b] for a, b, below in runs(kept, scarce) if below]
    states = sorted({int(d.state) for d in kept if d.state is not None})
    by_state = {}
    for state in states:
        spreads = [d.spread_bps for d in kept if d.state is not None and int(d.state) == state]
        by_state[str(state)] = {"label": STATE_LABELS[state], "n": len(spreads),
                                "above": {str(t): rate_cell([int(exceeds_bp(s, t)) for s in spreads]) for t in taus}}
    # The last year's own days by state (#267): the whole-period table pools years in which the
    # state was mostly abundant, so a year spent in tight or scarce is shown on its own row.
    last_year = kept[-1].day.year
    year_n = {str(state): sum(1 for d in kept if d.day.year == last_year and d.state is not None
                              and int(d.state) == state) for state in states}
    rises = {}
    for t in taus:
        rates = [by_state[str(k)]["above"][str(t)]["rate"] for k in states]
        rises[str(t)] = all(b >= a for a, b in zip(rates, rates[1:]))
    last = kept[-1].day
    spans_held = [{"name": tier.name, "start": tier.start.isoformat(), "end": tier.end.isoformat() if tier.end else None}
                  for tier in locked if tier.end is None or tier.end > last]
    data = {
        "spans": spans, "buffer_spans": buffer_spans, "labels": {str(k): v for k, v in STATE_LABELS.items()},
        "band": list(SATIATION_BAND), "buffer_bn": ON_RRP_BUFFER_BN, "break_bn": ON_RRP_DEPLETION_BREAK_BN,
        "by_state": by_state, "last_year": {"year": last_year, "days_by_state": year_n},
        "rises": rises, "taus": taus, "held_out": spans_held,
        "status": {k: status[k] for k in ("key", "icon", "word")},
        "counted": {"first": kept[0].day.isoformat(), "last": last.isoformat(), "n": len(kept),
                    "unknown": sum(1 for d in kept if d.state is None)},
        "bootstrap": {"method": "stationary", "block_length": BOOTSTRAP_BLOCK_LENGTH, "level": BOOTSTRAP_LEVEL,
                      "replications": BOOTSTRAP_REPLICATIONS, "seed": BOOTSTRAP_SEED},
    }

    def share(state, t):
        c = by_state[str(state)]
        a = c["above"][str(t)]
        return f"{pct(a['rate'])} of {c['label']} days ({a['k']} of {c['n']})"

    t = taus[0]
    if rises[str(t)]:
        caption = (f"Here the share of days more than +{t} bp above IORB rises with the state, from "
                   f"{share(states[0], t)} to {share(states[-1], t)}. The band describes the period; no forecast "
                   f"on this page reads it.")
    else:
        drops = []
        for a, b in zip(states, states[1:]):
            ca, cb = by_state[str(a)]["above"][str(t)], by_state[str(b)]["above"][str(t)]
            if cb["rate"] < ca["rate"]:
                overlap = cb["interval"][1] >= ca["interval"][0]
                drops.append(f"on {share(a, t)} but {share(b, t)}" + (", and the intervals overlap" if overlap else ""))
        caption = (f"Pressure-day frequency does not rise step by step with the state. SOFR closed more than +{t} bp "
                   f"above IORB {'; and '.join(drops)}. The band describes the period. It is not a working indicator, "
                   f"and no forecast on this page reads it.")
    level = round(100 * BOOTSTRAP_LEVEL)
    head = "".join(f"<th scope='col'>Above +{t} bp</th>" for t in taus)
    body = "".join(
        f"<tr><th scope='row'>{k} {by_state[str(k)]['label']}</th><td>{days(by_state[str(k)]['n'])}</td>"
        + "".join(f"<td>{pct(by_state[str(k)]['above'][str(t)]['rate'])} ({by_state[str(k)]['above'][str(t)]['k']} "
                  f"of {by_state[str(k)]['n']}); {level}% interval "
                  f"{pct(by_state[str(k)]['above'][str(t)]['interval'][0])} to "
                  f"{pct(by_state[str(k)]['above'][str(t)]['interval'][1])}</td>" for t in taus)
        + "</tr>" for k in states)
    body += (f"<tr><th scope='row'>{last_year} only</th><td colspan='{1 + len(taus)}'>days by state, "
             + " / ".join(f"{k} {year_n[str(k)]}" for k in states) + "</td></tr>")
    low, high = SATIATION_BAND
    brk = f"${ON_RRP_BUFFER_BN:,.0f}bn"
    held = (f" Days from {day(spans_held[0]['start'])} on are {held_as(h['name'] for h in spans_held)}: "
            f"the band is not drawn on them and they are in no "
            f"share here." if spans_held else "")
    fills = {
        "band_status": (f"<span class='bandchip'><span aria-hidden='true'>{status['icon']}</span> {status['word']}</span> "
                        f"on the <a href='#n4'>market map</a>: {status['reason']}"),
        "band_caption": caption,
        "band_first": day(kept[0].day.isoformat()), "band_last": day(last.isoformat()),
        "band_held_note": held.strip() or "No day in the band is held out.",
        "band_break": brk,
        "band_key": "".join(f"<li class='s{k}'><i aria-hidden='true'></i>{k} {v}</li>" for k, v in STATE_LABELS.items()),
        "band_table": (f"<table><caption>Share of days above each headline line, by state, {day(kept[0].day.isoformat())}"
                       f" to {day(last.isoformat())}</caption><thead><tr><th scope='col'>State</th>"
                       f"<th scope='col'>Days</th>{head}</tr></thead><tbody>{body}</tbody></table>"),
        "band_read": (
            f"The state adds two readings. Reserves over the total assets of all commercial banks: 0 at or above "
            f"{round(100 * high)}%, 1 from {round(100 * low)}% up to it, 2 below {round(100 * low)}%. "
            f"{link(notes['claims']['reserve_ratio'])} And the overnight reverse repo balance: 0 at or above "
            f"{brk}, 1 below it. The sum runs from 0 to {len(STATE_LABELS) - 1}: {'; '.join(f'{k} {v}' for k, v in STATE_LABELS.items())}."),
        "band_asof": (
            f"Each day shows the state as it could be read at {clock(decision)} New York time that day, from the "
            f"latest week all its inputs were public. {link(notes['claims']['h8_release'])} Bank assets are each "
            f"week's first print. Reserves are the latest revised figures, so that leg is shown with hindsight."),
        "band_interval": (f"Each interval is a {level}% stationary-bootstrap interval that resamples a state's days in "
                          f"blocks averaging {BOOTSTRAP_BLOCK_LENGTH} days, the one #115's validation used."),
    }
    return data, fills


def n2_bin(spread, taus):
    """How many thresholds a spread is strictly above: 0 at or below the first, len(taus) above the last.

    The bins are exclusive, so a day above the top threshold is drawn once, in
    the top bin, not also as a day above each lower one.
    """
    return sum(1 for tau in taus if spread > tau)


def newcomer_n2(rows, registry, decision, locked, thresholds):
    """N2 "Why is this hard?": every scored day, binned by the highest threshold it crossed.

    The day set is the scored grid, `asof.fold_grid` at `N2_MINIMUM_HISTORY`.
    Days in a lockbox tier not yet opened are listed by date only, with no
    spread and no bin, so the chart draws them hollow and grey, labelled "held
    out", and nothing this view writes can depend on their values. Every count,
    share and sentence is computed from `counted(scored, locked)`. The headline
    thresholds (the first two) get a count and a share; days above the upper two
    are drawn and listed one by one, with no rate and no pooled statement (#141
    §4).
    """
    taus = [int(t) for t in thresholds["taus_bp"]]
    pressure_bp, second_bp = taus[0], taus[1]
    dates = [date.fromisoformat(r["date"]) for r in rows]
    grid = fold_grid(dates, registry, decision_time=decision, minimum_history=N2_MINIMUM_HISTORY)
    scored = [rows[i] for i in grid]
    kept = counted(scored, locked)
    if not kept:
        raise VisualError("every scored day is held out; N2 has nothing to count")
    open_days = {r["date"] for r in kept}
    for r in kept:
        r["n2_s"] = int((Decimal(r["sofr"]) - Decimal(r["iorb"])) * 100)
        r["n2_b"] = n2_bin(r["n2_s"], taus)
    days_out = [[r["date"], r["n2_s"], r["n2_b"]] if r["date"] in open_days else [r["date"], None, None]
                for r in scored]
    bins = [sum(1 for r in kept if r["n2_b"] == b) for b in range(len(taus) + 1)]
    above = [sum(bins[b:]) for b in range(1, len(taus) + 1)]  # days strictly above each threshold
    by_year = {}
    for r in kept:
        if r["n2_b"] >= 1:
            by_year[int(r["date"][:4])] = by_year.get(int(r["date"][:4]), 0) + 1
    clusters = cluster_years(by_year)
    rest = sorted(set(by_year) - set(clusters))
    # A run: a pressure day whose previous scored day was counted and also a pressure day.
    runs = sum(1 for prev, r in zip(scored, scored[1:])
               if prev["date"] in open_days and r["date"] in open_days and prev["n2_b"] >= 1 and r["n2_b"] >= 1)
    tail = [{"date": r["date"], "s": r["n2_s"], "bin": r["n2_b"]} for r in kept if r["n2_b"] >= 3]
    spans = held_out_spans(scored, locked)
    n = len(kept)
    share = lambda k: f"{k:,} ({round(100 * k / n)}%)"
    data = {
        "taus": taus, "held_out": spans, "minimum_history": N2_MINIMUM_HISTORY,
        "scored": {"first": scored[0]["date"], "last": scored[-1]["date"], "n": len(scored)},
        "counted": {"first": kept[0]["date"], "last": kept[-1]["date"], "n": n, "bins": bins,
                    "above": above, "by_year": {str(y): k for y, k in sorted(by_year.items())},
                    "cluster_years": clusters, "runs": runs},
        "days": days_out, "tail": tail,
    }
    fills = {
        "n2_lede": (f"Of the {n:,} business days scored from {day(kept[0]['date'])} to {day(kept[-1]['date'])}, "
                    f"SOFR closed more than +{pressure_bp} bp above IORB on {share(above[0])} and more than "
                    f"+{second_bp} bp above on {share(above[1])}. "
                    + (f"Most of the days above +{pressure_bp} bp came in {year_list(clusters)}" if clusters
                       else f"No day was above +{pressure_bp} bp")
                    + (f"; the rest in {year_list(rest)}." if rest else ".")),
        "n2_first": day(scored[0]["date"]), "n2_last": day(scored[-1]["date"]),
        "n2_panel_first": day(rows[0]["date"]),
        "n2_min_history": f"{N2_MINIMUM_HISTORY:,}",
        "n2_quiet": f"{n - above[0]:,} of the {n:,}",
        "n2_runs": (f"Of the {above[0]:,} days above +{pressure_bp} bp, {runs:,} came on the business day after "
                    f"another one." if above[0] else ""),
        "n2_tail_list": "".join(
            f"<li><time>{short_day(e['date'])}</time> {bp(e['s'])} bp</li>" for e in tail),
        "n2_held_note": (
            "Hollow grey marks: the scored days " + " and ".join(
                f"from {day(h['start'])} to {day(h['end'])}" for h in spans)
            + ", " + held_as(h["name"] for h in spans) + ". "
            "They are drawn without their spread and left out of every count and sentence in this view."
            if spans else "No scored day is held out."),
    }
    for b in range(1, len(taus) + 1):
        fills[f"n2_tau{b}"] = taus[b - 1]
    return data, fills


# ---------------------------------------------------------------- N5 "A quarter-end squeeze, step by step" (#146)


def n5_snapshots(repo):
    """N5's snapshot series: `({key: {"source", "field", "by_ref": {ref_date: (available_at, value)}}}, {path: sha256})`."""
    out, digests = {}, {}
    for key, (root, source, series_id) in N5_SNAPSHOTS.items():
        results, snaps = snapshot_series(repo, root, series_id)
        out[key] = {"source": source, "field": series_id,
                    "by_ref": {ref: (at, value) for ref, at, value in results}}
        digests.update(snaps)
    return out, digests


def check_steps(tag_map, notes):
    """Refuse a walkthrough step the map cannot back: an unknown flow, board, tag or series, or an unsourced claim."""
    tags = {t["key"] for t in tag_map["tags"]}
    keys = set()
    for step in tag_map.get("steps", ()):
        key = step.get("key", "")
        if not re.fullmatch(r"[a-z0-9_]+", key) or key in keys:
            raise VisualError(f"map step {step} has no unique key")
        keys.add(key)
        for flow in step["flows"]:
            if flow not in tag_map["flows"]:
                raise VisualError(f"map step {key!r} highlights a flow {flow!r} the map does not draw")
        for board in step["boards"]:
            if board not in tag_map.get("boards", {}):
                raise VisualError(f"map step {key!r} highlights a board {board!r} the map does not draw")
        for tag in step["tags"]:
            if tag not in tags:
                raise VisualError(f"map step {key!r} rests on a tag {tag!r} the map does not carry")
        for series in step["series"]:
            if series not in N5_SERIES:
                raise VisualError(f"map step {key!r} draws a series {series!r} the generator does not know")
        if not step["claims"]:
            raise VisualError(f"map step {key!r} states no claim")
        for claim in step["claims"]:
            entry = notes["claims"].get(claim)
            if entry is None or not entry.get("src", "").startswith(ALLOWED_SOURCES):
                raise VisualError(f"map step {key!r} rests on no sourced claim {claim!r} in {ANNOTATIONS}")
    if not keys:
        raise VisualError(f"{MAP} lists no steps; N5 has nothing to walk through")


def n5_quarter_ends(rows, locked, on_rrp, registry, decision):
    """N5's two worked quarter-ends, chosen by `N5_QUARTER_END_RULE` from inputs known in advance.

    Reads only `N5_RULE_COLUMNS` of each row and the ON RRP results, never a
    rate. A quarter-end's reading is the one public at its decision instant: the
    declared decision time on the panel day before it. Days in a locked tier are
    never chosen. Returns `{"scarce": q, "abundant": q}`, each q
    `{"date", "decision_day", "on_rrp": {"ref", "bn"}}`.
    """
    before, below = N5_QUARTER_END_RULE["before"], N5_QUARTER_END_RULE["scarce_below_bn"]
    found = []
    for i, r in enumerate(rows):
        if r["quarter_end"] != "1" or i == 0 or r["date"] >= before:
            continue
        if locked_tier(date.fromisoformat(r["date"]), locked) is not None:
            continue
        ref, value = on_rrp_as_of(on_rrp, date.fromisoformat(rows[i - 1]["date"]), decision, registry)
        found.append((value, {"date": r["date"], "decision_day": rows[i - 1]["date"],
                              "on_rrp": {"ref": ref.isoformat(), "bn": round(float(value), 3)}}))
    scarce = [q for value, q in found if value < below]
    if not scarce:
        raise VisualError(f"no quarter-end before {before} read ON RRP below ${below:,.0f}bn; N5 has no scarce case")
    abundant = max(found, key=lambda o: o[0])[1]
    return {"scarce": scarce[-1], "abundant": abundant}


def n5_read(read, row, snaps):
    """One read's value on one panel row, as a `Decimal`, or `None` where the source has none."""
    kind, key = read
    if kind == "panel":
        return Decimal(row[key]) if row.get(key) else None
    entry = snaps[key]["by_ref"].get(date.fromisoformat(row["date"]))
    return None if entry is None else Decimal(str(entry[1]))


def n5_available(read, rows, position, registry, snaps, zone):
    """When a read's value for `rows[position]` became public, as New York wall time (naive), or `None`.

    A snapshot read is public no earlier than its source's registry declaration
    counted on the panel's dates: the adapter's `available_at` counts weekdays
    and does not know market holidays (#201).
    """
    kind, key = read
    dates = [date.fromisoformat(r["date"]) for r in rows]
    if kind == "snapshot":
        entry = snaps[key]["by_ref"].get(dates[position])
        if entry is None:
            return None
        adapter = entry[0].astimezone(zone).replace(tzinfo=None)
        declared = declared_availability(registry, snaps[key]["source"], snaps[key]["field"], dates, position)
        return adapter if declared is None else max(adapter, declared)
    ats = [declared_availability(registry, source, field, dates, position) for source, field in FEATURE_FIELDS[key]]
    ats = [at for at in ats if at is not None]
    return max(ats) if ats else None


def n5_when(at, today):
    """When the value for `today` became public, in words, counted from the day and never naming a later date.

    A later date may fall in a locked tier, so the sentence gives the gap, not the date.
    """
    gap = (at.date() - today).days
    when = f"at {clock(at.time())} New York time"
    if gap < 0:
        return f"was announced {-gap} calendar {'day' if gap == -1 else 'days'} before it, {when}"
    if gap == 0:
        return f"was public the same day, {when}"
    return f"was public {gap} calendar {'day' if gap == 1 else 'days'} later, {when}"


def n5_series(rows, quarter_ends, registry, decision, snaps):
    """Each N5 series over each worked window: its values, which of them were public at the decision, its clock.

    `quarter_ends[kind]["days"]` lists the window's panel positions and whether
    each is held out. A held-out day has no value. A value is "known" when every
    read behind it was public at the decision instant, the declared decision
    time on the panel day before the quarter-end; `known` is the last such
    offset in the window.
    """
    zone = ZoneInfo(registry[NYFED_ON_RRP_SOURCE_ID]["release_lag"]["timezone"])
    out = {}
    for key, spec in N5_SERIES.items():
        entry = {"label": spec["label"], "unit": spec["unit"], "mode": spec["mode"],
                 "hindsight": bool(spec.get("hindsight")), "values": {}, "known": {}, "public_offsets": {},
                 "clock": {}}
        for kind, q in quarter_ends.items():
            instant = datetime.combine(date.fromisoformat(q["decision_day"]), decision)
            values, public = [], []
            for d in q["days"]:
                if d["held"]:
                    values.append(None)
                    continue
                row = rows[d["position"]]
                reads = [n5_read(read, row, snaps) for read in spec["reads"]]
                if any(v is None for v in reads):
                    values.append(None)
                    continue
                if spec["unit"] == "bp":
                    values.append(int((reads[0] - reads[1]) * 100))
                else:
                    values.append(float(reads[0]))
                ats = [n5_available(read, rows, d["position"], registry, snaps, zone) for read in spec["reads"]]
                if any(at is None for at in ats):
                    raise VisualError(f"N5's {key} declares no publication time for {row['date']}")
                if all(at <= instant for at in ats):
                    public.append(d["offset"])
                if d["offset"] == 0:
                    entry["clock"][kind] = n5_when(max(ats), date.fromisoformat(row["date"]))
            if spec["mode"] == "change":
                base = next((v for v in values if v is not None), None)
                values = [None if v is None else v - base for v in values]
            entry["values"][kind] = [v if v is None or isinstance(v, int) else round(v, 3) for v in values]
            entry["public_offsets"][kind] = public
            entry["known"][kind] = max(public) if public else None
        out[key] = entry
    return out


def n5_value(v, unit, mode):
    if v is None:
        return "&ndash;"
    if unit == "bp":
        return bp(v)
    text = f"{abs(v):,.0f}"
    return (("+" if v > 0 else "−" if v < 0 else "") + text) if mode == "change" else text


def newcomer_n5(rows, locked, chosen, registry, decision, snaps, tag_map, tags, notes):
    """N5 "A quarter-end squeeze, step by step" (#146): the map's flows in order, with a chart per step.

    `chosen` is `n5_quarter_ends(...)`. Each quarter-end's window is
    `N5_WINDOW_BUSINESS_DAYS` panel days either side of it. A day in a locked
    tier is listed by date only, with no value, and is in no sentence. `tags`
    are N4's derived tag rows: a step shows each tag's status, and a step with
    no series says so from the same derivation, and is refused once its tag's
    data is tracked.
    """
    check_steps(tag_map, notes)
    index = {r["date"]: i for i, r in enumerate(rows)}
    quarter_ends = {}
    for kind, q in chosen.items():
        i = index[q["date"]]
        days = []
        for position in range(max(0, i - N5_WINDOW_BUSINESS_DAYS), min(len(rows), i + N5_WINDOW_BUSINESS_DAYS + 1)):
            today = date.fromisoformat(rows[position]["date"])
            held = locked_tier(today, locked) is not None
            days.append({"date": rows[position]["date"], "offset": position - i, "held": held, "position": position})
        quarter_ends[kind] = dict(q, days=days)
    series = n5_series(rows, quarter_ends, registry, decision, snaps)
    for q in quarter_ends.values():
        for d in q["days"]:
            del d["position"]
    by_tag = {t["key"]: t for t in tags}
    marks = {k: (i, w) for k, i, w in STATUSES}
    steps, panels, items = [], [], []
    n = len(tag_map["steps"])
    for number, step in enumerate(tag_map["steps"], 1):
        mine = [by_tag[t] for t in step["tags"]]
        if not step["series"]:
            tracked = [t["key"] for t in mine if t["data_in_repo"]]
            if tracked:
                raise VisualError(f"map step {step['key']!r}: data for {tracked} is tracked in the repository; "
                                  f"draw it rather than say there is none")
        chips = "".join(
            f'<span class="tagchip"><span aria-hidden="true">{marks[t["status"]][0]}</span> {html.escape(t["label"])} '
            f'<small>{marks[t["status"]][1]}</small></span>' for t in mine)
        hypothesis = step.get("hypothesis")
        under_test = (f'<p class="hyp"><b>Hypothesis under test</b> in <a href="https://github.com/{REPOSITORY}/'
                      f'issues/{hypothesis}">#{hypothesis}</a>, not a finding: that the top of the day&rsquo;s '
                      f'trades moves before the middle does. Daily data cannot show the order within a day.</p>'
                      if hypothesis else "")
        claims = " ".join(link(notes["claims"][c]) for c in step["claims"])
        if step["series"]:
            clocks = []
            for key in step["series"]:
                s = series[key]
                name = s["label"] + (" less IORB" if s["unit"] == "bp" else "")
                said = "; ".join(f"the value for {day(chosen[kind]['date'])} {s['clock'][kind]}"
                                 for kind in ("scarce", "abundant") if kind in s["clock"])
                late = " From FRED's latest vintage, so shown with hindsight." if s["hindsight"] else ""
                clocks.append(f"<li><b>{html.escape(name)}</b>: {said}.{late}</li>")
            body = f'<ul class="clocks">{"".join(clocks)}</ul>'
        else:
            reasons = "; ".join(f"{html.escape(t['label'])}: {t['reason']}" for t in mine)
            body = f'<p class="nodata">There is no public series in this repository yet for this step ({reasons}).</p>'
        panels.append(
            f'<div class="n5p" id="n5p-{step["key"]}" role="group" aria-labelledby="n5p-{step["key"]}-h"'
            f'{"" if number == 1 else " hidden"}><h3 id="n5p-{step["key"]}-h">Step {number} of {n}: '
            f'{html.escape(step["title"])}</h3>{under_test}<p>{claims}</p><div class="chips">{chips}</div>{body}</div>')
        items.append(f'<li><button type="button" class="n5step" data-step="{number - 1}" aria-controls="n5p-{step["key"]}"'
                     f'{" aria-current=" + chr(34) + "step" + chr(34) if number == 1 else ""}>{html.escape(step["title"])}'
                     f'</button></li>')
        steps.append({"key": step["key"], "flows": list(step["flows"]), "boards": list(step["boards"]),
                      "series": list(step["series"]), "title": step["title"]})
    s, a = chosen["scarce"], chosen["abundant"]
    spread = series["spread"]

    def on_day(kind):
        q = quarter_ends[kind]
        v = spread["values"][kind][next(j for j, d in enumerate(q["days"]) if d["offset"] == 0)]
        return f"{bp(v)} bp"

    held = sorted(d["date"] for q in quarter_ends.values() for d in q["days"] if d["held"])
    below = f"${N5_QUARTER_END_RULE['scarce_below_bn']:,.0f}bn"
    before = N5_QUARTER_END_RULE["before"]

    def table(kind):
        q = quarter_ends[kind]
        head = "".join(f'<th scope="col">{short_day(d["date"])}' + (" (held out)" if d["held"] else "") + "</th>"
                       for d in q["days"])
        body = "".join(
            f'<tr><th scope="row">{html.escape(series[k]["label"])}, '
            f'{"bp over IORB" if series[k]["unit"] == "bp" else "$bn" + (", change" if series[k]["mode"] == "change" else "")}'
            f'</th>' + "".join(f"<td>{n5_value(v, series[k]['unit'], series[k]['mode'])}</td>" for v in series[k]["values"][kind])
            + "</tr>" for k in N5_SERIES)
        return (f'<div class="heat" role="region" aria-label="Table of the series around {day(q["date"])}" tabindex="0">'
                f'<table class="segtab"><caption>Around {day(q["date"])}, the quarter-end with cash '
                f'{kind}</caption><thead><tr><th scope="col">Series</th>{head}</tr></thead><tbody>{body}</tbody>'
                f'</table></div>')

    data = {"rule": dict(N5_QUARTER_END_RULE), "rule_columns": list(N5_RULE_COLUMNS),
            "window_business_days": N5_WINDOW_BUSINESS_DAYS, "quarter_ends": quarter_ends, "series": series,
            "steps": steps, "sources": {k: v[1] for k, v in N5_SNAPSHOTS.items()}}
    fills = {
        "n5_lede": (f"Two quarter-ends, chosen in advance by a rule that reads only the Fed's overnight reverse repo "
                    f"balance: {day(s['date'])}, with cash scarce, and {day(a['date'])}, with cash abundant. SOFR less "
                    f"IORB closed at {on_day('scarce')} on the first and {on_day('abundant')} on the second. Step "
                    f"through what the Fed and its staff describe happening around a quarter-end, and what each "
                    f"public series did then."),
        "n5_rule": (f"The scarce case is the most recent quarter-end before {day(before)} on which the ON RRP result "
                    f"public at the {clock(decision)} decision the business day before was below {below}: "
                    f"{day(s['date'])}, which read ${s['on_rrp']['bn']:,.1f}bn. The abundant case is the quarter-end "
                    f"before then with the largest such result: {day(a['date'])}, which read "
                    f"${a['on_rrp']['bn']:,.0f}bn. The rule never reads a rate or a spread"),
        "n5_window": word(N5_WINDOW_BUSINESS_DAYS),
        "n5_decision": clock(decision),
        "n5_map": map_svg(tag_map, tags, {k: html.escape(v) for k, v in tag_map["parties"].items()}, prefix="n5"),
        "n5_step_list": f'<ol class="n5list" aria-label="Steps">{"".join(items)}</ol>',
        "n5_panels": "".join(panels),
        "n5_held_note": (f"Days from {day(held[0])} on are "
                         f"{held_as(locked_tier(date.fromisoformat(d), locked).name for d in held)}: "
                         f"they are drawn greyed, without their "
                         f"values, and are in no sentence here." if held else "No day in these charts is held out."),
        "n5_table": table("scarce") + table("abundant"),
    }
    return data, fills


# ---------------------------------------------------------------- the final test (#238)


def rests_on(window, interval, mean, rel):
    """What the primary cell's pass rests on (#238, hold ruling): computed after the result, decides nothing.

    The two days with the largest paired difference, their share of the summed difference, the mean and interval
    of the rest under the record's own bootstrap (block length, seed, replications, level), and how many days
    the published model won. Read off `window_per_origin`; nothing is typed.
    """
    diffs = [r["difference_bps"] for r in window]
    if len(diffs) < 5:
        raise VisualError(f"{rel}: window_per_origin has {len(diffs)} days, too few to ask what a pass rests on")
    top = sorted(range(len(diffs)), key=lambda i: -diffs[i])[:2]
    total = sum(diffs)
    if total <= 0:
        raise VisualError(f"{rel}: the summed paired difference is not positive, so a share of it is undefined")
    if abs(total / len(diffs) - mean) > 1e-9:
        raise VisualError(f"{rel}: window_per_origin does not average to the cell's mean_difference_bps")
    rest = [v for i, v in enumerate(diffs) if i not in top]
    lower, upper = stationary_bootstrap_interval(
        lambda ix: sum(rest[i] for i in ix) / len(ix), len(rest), block_length=interval["block_length"],
        seed=interval["seed"], replications=interval["replications"], level=interval["level"])
    ordered = sorted(top, key=lambda i: window[i]["scored_date"])
    return {"days": [window[i]["scored_date"] for i in ordered], "values": [diffs[i] for i in ordered],
            "share": sum(diffs[i] for i in top) / total, "mean": sum(rest) / len(rest), "lower": lower,
            "upper": upper, "block_length": interval["block_length"], "seed": interval["seed"],
            "replications": interval["replications"], "wins": sum(v > 0 for v in diffs), "n": len(diffs)}


def final_test(records, locked):
    """The "Final test" section (#238), read off `FINAL_TEST` alone.

    Every figure goes through `from_record`. The verdict is the record's
    result, stated next to the near-blind disclosure; the claim is the record's
    pre-registered sentence, quoted only on a pass. The split by day type
    decides nothing, and a cell the record gives no interval says so. The CRPS
    cells at h = 2 to 5 each carry their verbatim label from the record (#229).
    """
    rel = FINAL_TEST

    def get(*keys):
        return from_record(records, rel, *keys)

    cell = ("primary", "cell")
    result = get(*cell, "result")
    if result not in ("pass", "fail"):
        raise VisualError(f"{rel}: the primary cell's result is {result!r}, neither pass nor fail")
    persistence, published = get(*cell, "crps_persistence_bps"), get(*cell, "crps_published_bps")
    mean, lower, upper = get(*cell, "mean_difference_bps"), get(*cell, "interval", "lower"), get(*cell, "interval", "upper")
    level = round(100 * get(*cell, "interval", "level"))
    first, last, n = get(*cell, "first"), get(*cell, "last"), get(*cell, "days")
    if (result == "pass") != (lower > 0):
        raise VisualError(f"{rel}: the result {result!r} does not match its interval {lower} to {upper}")
    claim = get("primary", "claim")
    opened = get("opened", "date")
    checksum = get("crps_declaration_sha256")
    prereg = get("pre_registration")

    by_type = get(*cell, "splits", "by_day_type")
    split = []
    for key in FINAL_TEST_DAY_TYPES:
        if key not in by_type:
            raise VisualError(f"{rel} carries no day type {key!r}")
        g = cell + ("splits", "by_day_type", key)
        row = {"key": key, "label": DAY_TYPES[key], "count": get(*g, "count"), "mean": get(*g, "mean")}
        if "interval" in by_type[key]:
            row["lower"], row["upper"] = get(*g, "interval", "lower"), get(*g, "interval", "upper")
        split.append(row)
    regimes = [k for k, v in get(*cell, "splits", "by_regime").items() if v.get("count")]

    h1 = [d for d in get("events_reported_only") if d.get("horizon") == 1]
    if len(h1) != 1:
        raise VisualError(f"{rel} carries {len(h1)} event documents at h = 1, not one")
    if "minimum_events" not in h1[0]:
        raise VisualError(f"{rel}: the h = 1 event document carries no minimum_events")
    stress = []
    for key, name in FINAL_TEST_STRESS_TARGETS:
        entry = h1[0].get("targets", {}).get(key, {}).get("all_days")
        if entry is None:
            raise VisualError(f"{rel} carries no h = 1 event cell {key!r}")
        labels = sorted({p["label"] for p in entry["paired"].values()})
        stress.append({"target": name, "events": entry["events"], "labels": labels})

    later = []
    for node in get("crps_reported_only"):
        if "interval" not in node:
            raise VisualError(f"{rel}: the CRPS cell at h = {node.get('horizon')} carries no interval")
        later.append({"horizon": node["horizon"], "days": node["days"], "persistence": node["crps_persistence_bps"],
                      "published": node["crps_published_bps"], "mean": node["mean_difference_bps"],
                      "lower": node["interval"]["lower"], "upper": node["interval"]["upper"],
                      "verdict": FINAL_TEST_LABELS[node["verdict"]], "label": node["verdict_label"]})

    rests = rests_on(get("primary", "window_per_origin"), get(*cell, "interval"), mean, rel)

    x, y = date.fromisoformat(first), date.fromisoformat(last)
    window = (f"{x.day} {x:%B} to {day(last)}" if x.year == y.year else f"{day(first)} to {day(last)}")
    gap = f"{signed(lower, 2)} to {signed(upper, 2)} bp"
    near_blind = ("near-blind, not blind: these days had appeared inside earlier pooled results, though the record "
                  "says no choice was made on them by name")
    if result == "pass":
        verdict = (f"From {window}, the model's next-day forecast of the range of SOFR − IORB was more accurate "
                   f"than carrying the latest spread forward: {published:.2f} bp against {persistence:.2f} bp of "
                   f"CRPS, where lower is better, and the {level}% interval of the gap, {gap}, lies above zero. "
                   f"Result: <b>pass</b>, on a test that is {near_blind}.")
        claim_html = (f"<p class='ftclaim'><b>The claim, as pre-registered:</b> {html.escape(claim)}. It is a pass "
                      f"on a near-blind test, and a statement about the range forecast, not a warning of stress.</p>")
    else:
        verdict = (f"From {window}, the model's next-day forecast of the range of SOFR − IORB was not shown to be "
                   f"more accurate than carrying the latest spread forward: {published:.2f} bp against "
                   f"{persistence:.2f} bp of CRPS, where lower is better, with a {level}% interval for the gap of "
                   f"{gap}. Result: <b>fail</b>, on a test that is {near_blind}. No claim is made.")
        claim_html = ""

    def interval_cell(row):
        if "lower" not in row:
            return "<td>too few days for an interval</td>"
        return f"<td>{signed(row['lower'], 3)} to {signed(row['upper'], 3)}</td>"

    split_rows = "".join(
        f"<tr><th scope='row'>{r['label']}</th><td>{r['count']}</td><td>{signed(r['mean'], 3)}</td>{interval_cell(r)}</tr>"
        for r in split)
    split_table = (f"<div class='heat' role='region' aria-label='The final test by type of day' tabindex='0'>"
                   f"<table class='fttab'><caption>By type of day. This split decides nothing.</caption><thead><tr>"
                   f"<th scope='col'>Day type</th><th scope='col'>Days</th><th scope='col'>Mean difference, bp</th>"
                   f"<th scope='col'>{level}% interval, bp</th></tr></thead><tbody>{split_rows}</tbody></table></div>")
    later_rows = "".join(
        f"<tr data-h=\"{c['horizon']}\"><th scope='row'>{c['horizon']} days</th><td>{c['days']}</td>"
        f"<td>{c['persistence']:.3f}</td><td>{c['published']:.3f}</td>"
        f"<td>{signed(c['mean'], 3)} ({signed(c['lower'], 3)} to {signed(c['upper'], 3)})</td>"
        f"<td>{c['verdict']}; {html.escape(c['label'])}</td></tr>" for c in later)
    later_table = (f"<div class='heat' role='region' aria-label='CRPS at two to five days ahead, not evidence' "
                   f"tabindex='0'><table class='fttab'><caption>CRPS further ahead, reported only and not evidence"
                   f"</caption><thead><tr><th scope='col'>Ahead</th><th scope='col'>Days</th>"
                   f"<th scope='col'>Persistence, bp</th><th scope='col'>Model, bp</th>"
                   f"<th scope='col'>Difference ({level}% interval), bp</th><th scope='col'>Label</th></tr></thead>"
                   f"<tbody>{later_rows}</tbody></table></div>")

    def labels(entry):
        return " and ".join(entry["labels"])

    same = len({tuple(e["labels"]) for e in stress}) == 1
    cells = " and ".join(f"{e['target']} bp" for e in stress)
    stress_text = (
        f"<b>It is not a warning of stress.</b> It grades the forecast range, not the chance of pressure. One day "
        f"ahead, the event cells for days more than {cells} above IORB are "
        + (f"{labels(stress[0])}, with {' and '.join(str(e['events']) for e in stress)} such days in the window."
           if same else "; ".join(f"{e['target']} bp: {labels(e)}, with {e['events']} such days" for e in stress) + ".")
        + f" Below {h1[0]['minimum_events']} such days, a cell is labelled inconclusive.")
    rests_text = (f"<b>What the pass rests on, post hoc.</b> Two days carry {100 * rests['share']:.1f}% of the summed "
                  f"paired difference: {' and '.join(day(d) for d in rests['days'])} "
                  f"({' and '.join(signed(v, 2) + ' bp' for v in rests['values'])}). Without them the mean paired "
                  f"difference is {signed(rests['mean'], 3)} bp, {level}% interval {signed(rests['lower'], 3)} to "
                  f"{signed(rests['upper'], 3)} bp, by the record's own bootstrap (mean block length "
                  f"{rests['block_length']}, seed {rests['seed']}, {rests['replications']:,} replications), which "
                  f"{'does not separate it from zero' if rests['lower'] <= 0 <= rests['upper'] else 'lies on one side of zero'}. "
                  f"The model beat persistence on {rests['wins']} of {rests['n']} days. On this near-blind test, "
                  f"this was computed after the result: it decides nothing, and the verdict stands.")
    blind = min(locked, key=lambda t: t.start) if locked else None
    blind_text = (f" A blind test waits on the days from {day(blind.start.isoformat())} on: "
                  f"the {blind.name.replace('_', '-')} tier, which no test has opened." if blind else "")
    regime_text = (f"every scored day falls in one regime, {dash(regimes[0])}" if len(regimes) == 1
                   else f"the scored days fall in {word(len(regimes))} regimes, {', '.join(map(dash, regimes))}")
    data = {"record": rel, "result": result, "first": first, "last": last, "days": n, "level": level,
            "persistence": persistence, "published": published, "mean": mean, "lower": lower, "upper": upper,
            "by_day_type": split, "regimes": regimes, "stress": stress, "later": later, "rests": rests}
    fills = {
        "ft_verdict": verdict,
        "ft_claim": claim_html,
        "ft_days": f"{n:,}",
        "ft_level": level,
        "ft_window": window,
        "ft_split_table": split_table,
        "ft_fixed": (f"<b>Fixed first.</b> The design, the benchmark and the command were written down and "
                     f"checksummed (<code>{checksum[:12]}</code>) before any of these days was scored "
                     f"(<a href='{BLOB}{prereg}'>the pre-registration</a>)."),
        "ft_once": f"<b>Run once,</b> on {day(opened)}, on Eleonora's go, and published whatever it showed.",
        "ft_benchmark": ("<b>Against carrying the latest spread forward.</b> The benchmark, as-of persistence, "
                         "forecasts the next day from the latest spread known at the decision time. Both are graded "
                         "by CRPS: how far a forecast range was from the spread that actually came, in basis "
                         "points, so lower is better."),
        "ft_switch": (f"<b>The deciding comparison was changed before the test was opened.</b> On 4 October 2026 the "
                      f"deciding cell was changed from the plain-leap probability cell (#216) to this CRPS cell, "
                      f"under Eleonora's ruling on #221, recorded in <a href='{BLOB}{prereg}'>the pre-registration</a>'s amendment."),
        "ft_rests": rests_text,
        "ft_not_stress": stress_text,
        "ft_not_blind": f"<b>It is near-blind, not blind.</b> These days had appeared inside earlier pooled results, "
                        f"though the record says no choice was made on them by name.{blind_text}",
        "ft_calm": (f"<b>2026 was calm,</b> and was known to be calm when the test was designed; {regime_text}. "
                    f"The test says nothing about a stressed period."),
        "ft_later": (f"<b>CRPS two to five days ahead is not evidence.</b> Those cells use a different model from "
                     f"the one-day forecast, and each carries Eleonora's label."),
        "ft_later_table": later_table,
        "ft_links": (f"The record: <a href='{BLOB}{rel}'><code>{rel}</code></a>. The write-up: "
                     f"<a href='{BLOB}docs/final-test.md'><code>docs/final-test.md</code></a>. The design: "
                     f"<a href='{BLOB}{prereg}'><code>{prereg}</code></a>."),
    }
    return data, fills


# ---------------------------------------------------------------- the page


def generate(repo, commit=None):
    """Return {relative path: bytes} for every output. Writes nothing."""
    repo = Path(repo)
    manifest = read_json(MANIFEST, repo)
    registry = read_json(SOURCES, repo)
    notes = read_json(ANNOTATIONS, repo)
    thresholds = read_json(THRESHOLDS, repo)
    regimes = read_json(SPLITS, repo)["regimes"]
    windows = read_json(EVENTS, repo)["windows"]
    glossary = read_json(GLOSSARY, repo)
    tag_map = read_json(MAP, repo)
    snapshot = read_json(ISSUES, repo)
    declarations = run_record_declarations(repo)
    locked = locked_tiers(repo / LOCKBOX)
    check_annotations(notes)
    check_glossary(glossary)
    records = run_records(repo)
    model, model_fills = model_chapters(records, thresholds["taus_bp"][:2])
    final, final_fills = final_test(records, locked)
    pending = pending_figures(records)
    commit = commit or input_commit(repo)

    with tempfile.TemporaryDirectory() as tmp:
        raw, digest = build_panel(repo, manifest, tmp)
    if model["scored"]["panel"] != digest:
        raise VisualError(f"the exceedance records are scored on panel {model['scored']['panel'][:12]}, not the "
                          f"published {digest[:12]}; refusing")
    rows = list(csv.DictReader(raw.decode().splitlines()))
    check_reserve_units(rows)

    decision = time.fromisoformat(manifest["decision_time"])
    n1, n1_fills = newcomer_n1([dict(r) for r in rows], locked, thresholds, notes)
    n2, n2_fills = newcomer_n2([dict(r) for r in rows], registry, decision, locked, thresholds)
    on_rrp, on_rrp_snapshots = on_rrp_results(repo)
    n3, n3_fills = newcomer_n3([dict(r) for r in rows], locked, thresholds, registry, decision, on_rrp, notes)
    scored, band_snapshots = scarcity_days(repo, locked)
    hist, fills = history(rows, notes, thresholds, regimes, windows, locked)
    fills.update(use_limitation_fill(repo))
    fills.update(n1_fills)
    fills.update(n2_fills)
    fills.update(n3_fills)
    try:
        seg_days = segment_days(rows, locked, on_rrp, registry, decision)
    except ValueError as exc:
        raise VisualError(f"N4's segment chart: {exc}") from exc
    n4, n4_fills = newcomer_n4(tag_map, registry, manifest, declarations, snapshot, tracked_snapshots(repo), notes,
                               glossary, rows, seg_days, decision, locked)
    fills.update(n4_fills)
    tag = next((t for t in n4["tags"] if t["key"] == BAND_TAG), None)
    if tag is None:
        raise VisualError(f"the band's legend reads the map tag {BAND_TAG!r}, which map.json does not carry")
    icon, label = next((i, w) for k, i, w in STATUSES if k == tag["status"])
    band, band_fills = newcomer_band(scored, locked, thresholds, registry, decision, on_rrp,
                                     {"key": tag["status"], "icon": icon, "word": label, "reason": tag["reason"]}, notes)
    fills.update(band_fills)
    n5_snaps, n5_digests = n5_snapshots(repo)
    try:
        chosen = n5_quarter_ends(rows, locked, on_rrp, registry, decision)
    except VisualError:
        raise
    except ValueError as exc:
        raise VisualError(f"N5's quarter-end rule: {exc}") from exc
    n5, n5_fills = newcomer_n5([dict(r) for r in rows], locked, chosen, registry, decision, n5_snaps, tag_map,
                               n4["tags"], notes)
    fills.update(n5_fills)
    fills.update(dfn_fills(glossary))
    note = parse_note(repo, notes["implementation_note"])
    last = rows[-1]
    shown = counted(rows, locked)[-1]  # chapter 1 quotes the last day that is not held out
    iorb_shown = Decimal(shown["iorb"])
    plumbing = {
        "note": note,
        "day": shown["date"],
        "segments": [
            {"key": k, "rate": float(shown[k]), "vs_iorb_bp": int((Decimal(shown[k]) - iorb_shown) * 100),
             "text": notes["claims"]["segments_" + k]["text"], "src": notes["claims"]["segments_" + k]["src"]}
            for k in ("tgcr", "bgcr", "sofr")],
    }
    clock_rows = publication_clock(registry, manifest["built_columns"], decision)
    observed = [c for c in clock_rows if c["kind"] == "observed" and "read_lag" in c]
    stalest = max(observed, key=lambda c: (c["read_lag"], c["unit"] == "business_days"))
    freshest = min(observed, key=lambda c: (c["read_lag"], c["unit"] != "business_days"))
    sched = [c for c in clock_rows if c["kind"] == "scheduled"]
    srp = next(r for r in note["rates"] if r["key"] == "srp")
    rrp = next(r for r in note["rates"] if r["key"] == "rrp")
    c = notes["claims"]
    fills.update({
        "first_day": day(rows[0]["date"]), "last_day": day(last["date"]),
        "shown_day": day(shown["date"]),
        "shown_day_is": "the panel's last day" if shown is last else "the last day not held out",
        "latest_volume": f"${float(shown['sofr_volume']) / 1000:.1f} trillion",
        "n_rows": f"{len(rows):,}", "sha": digest, "sha12": digest[:12],
        "commit": commit, "commit12": commit[:12],
        "decision": clock(decision), "decision_24": decision.strftime("%H:%M"),
        "note_issued": day(note["issued"]), "note_effective": day(note["effective"]),
        "note_src": note["src"], "note_sha": note["sha256"], "note_retrieved": note["retrieved_at"],
        "srp_vs_iorb": bp(srp["vs_iorb_bp"]), "rrp_vs_iorb": bp(rrp["vs_iorb_bp"]),
        "c_segments_tgcr": link(c["segments_tgcr"]), "c_segments_bgcr": link(c["segments_bgcr"]),
        "c_segments_sofr": link(c["segments_sofr"]), "c_sofr_trim": link(c["sofr_trim"]),
        "c_sofr_publication": link(c["sofr_publication"]),
        "c_triparty_actors": link(c["triparty_actors"]), "c_cleared_actors": link(c["cleared_actors"]),
        "c_fed_cash": link(c["fed_cash"]), "c_standing_repo": link(c["standing_repo"]),
        "n_inputs": word(len({r["column"] for r in clock_rows if r["kind"] != "calendar"})),
        "n_calendar": word(sum(1 for r in clock_rows if r["kind"] == "calendar")),
        "lag_min": f"{days(freshest['read_lag'])} old",
        "lag_max": f"{lower_first(stalest['label'])}, {stalest['read_lag']} {stalest['unit'].replace('_', ' ')} old",
        "sched_names": " and ".join(sorted({r["label"].split(",")[0] for r in sched})) or "none",
        "process_list": "".join(f"<li><b>{p['step']}</b><span>{p['text']}. <a href='{p['src']}'>Rule</a></span></li>"
                                for p in notes["process"]),
        "guard_list": "".join(f"<li><b>{g['name']}.</b> {g['text']}. <a href='{g['src']}'>Source</a></li>"
                              for g in notes["guards"]),
        "validation": link(notes["validation"]),
        "lead_time_placeholder": pending["lead_time"],
    })
    fills.update(model_fills)
    fills.update(final_fills)

    inputs = {rel: sha256(repo / rel) for rel in
              (MANIFEST, SOURCES, EVENTS, THRESHOLDS, SPLITS, LOCKBOX, ANNOTATIONS, GLOSSARY, TEMPLATE,
               notes["implementation_note"]["path"])}
    provenance = {
        "commit": commit,
        "generator": "scripts/emit_visual.py",
        "panel": {"sha256": digest, "rows": len(rows), "first": rows[0]["date"], "last": last["date"],
                  "built_from": FIXTURES, "manifest": MANIFEST},
        "inputs": inputs,
    }
    build = {"process": notes["process"], "guards": notes["guards"], "validation": notes["validation"]}
    clock_data = {"decision_time": decision.strftime("%H:%M"), "inputs": clock_rows}
    model_provenance = dict(provenance, inputs={rel: sha256(repo / rel) for rel in records})
    payloads = {"history": hist, "plumbing": plumbing, "clock": clock_data, "build": build, "model": model,
                "newcomer_n1": n1, "newcomer_n2": n2, "newcomer_n3": n3, "newcomer_n4": n4, "newcomer_band": band,
                "newcomer_n5": n5, "final_test": final}
    # N3 also reads the holiday table (through `data.quarter_end_window`) and the ON RRP snapshots.
    n3_provenance = {**provenance, "inputs": {**inputs, HOLIDAYS: sha256(repo / HOLIDAYS), **on_rrp_snapshots}}
    n4_provenance = dict(provenance, inputs=dict(
        {rel: sha256(repo / rel) for rel in (MAP, ISSUES, SOURCES, MANIFEST, ANNOTATIONS, GLOSSARY)},
        **{rel: sha256(repo / rel) for rel in declarations}, **on_rrp_snapshots))
    # The band reads the measurement panel's extra snapshots; its legend's status is N4's, derived from N4's inputs.
    band_provenance = {**provenance, "status_from": f"{DATA_DIR}/newcomer_n4.json",
                       "inputs": {**inputs, "scripts/scarcity_validation.py":
                                  sha256(repo / "scripts/scarcity_validation.py"),
                                  MAP: sha256(repo / MAP), ISSUES: sha256(repo / ISSUES), **band_snapshots}}
    # N5 reads the ON RRP, SOFR and EFFR snapshots and the map's steps; its tag statuses are N4's.
    n5_provenance = {**provenance, "status_from": f"{DATA_DIR}/newcomer_n4.json",
                     "inputs": {**inputs, MAP: sha256(repo / MAP), ISSUES: sha256(repo / ISSUES),
                                **on_rrp_snapshots, **n5_digests}}
    final_provenance = dict(provenance, inputs={FINAL_TEST: sha256(repo / FINAL_TEST)})
    own = {"model": model_provenance, "final_test": final_provenance, "newcomer_n3": n3_provenance, "newcomer_n4": n4_provenance,
           "newcomer_band": band_provenance, "newcomer_n5": n5_provenance}
    out = {}
    for name, payload in payloads.items():
        doc = {"provenance": own.get(name, provenance), "data": payload}
        out[f"{DATA_DIR}/{name}.json"] = (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                                      ensure_ascii=False) + "\n").encode("utf-8")
    page_data = {k: payloads[k] for k in ("history", "plumbing", "clock", "model", "newcomer_n1", "newcomer_n2",
                                          "newcomer_n3", "newcomer_band", "newcomer_n5", "final_test")}
    page_data["n4_segments"] = n4["segments"]
    template = (repo / TEMPLATE).read_text(encoding="utf-8")
    fills["newcomer_nav"] = newcomer_nav(template)
    if "/*__DATA__*/null" not in template:
        raise VisualError("the template has no /*__DATA__*/null slot")
    page = template.replace("/*__DATA__*/null", json.dumps(page_data, sort_keys=True, separators=(",", ":"),
                                                            ensure_ascii=False).replace("</", "<\\/"))
    out[PAGE] = fill(page, fills).encode("utf-8")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true", help="write nothing; fail if an output is stale")
    parser.add_argument("--commit", help="stamp this commit instead of reading git history")
    parser.add_argument("--refresh-issues", action="store_true",
                        help=f"rewrite {ISSUES} from GitHub (network); nothing else is written")
    parser.add_argument("--repo", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    repo = Path(args.repo)
    if args.refresh_issues:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            data = refresh_issues(read_json(MAP, repo), gh_fetch, now)
        except VisualError as exc:
            sys.exit(f"emit_visual: {exc}")
        (repo / ISSUES).write_bytes(data)
        print(f"emit_visual: wrote {ISSUES}; regenerate the page with `python3 scripts/emit_visual.py`")
        return
    try:
        outputs = generate(repo, args.commit)
    except (VisualError, LookAheadError) as exc:
        sys.exit(f"emit_visual: {exc}")
    stale = [rel for rel, data in outputs.items()
             if not (repo / rel).exists() or (repo / rel).read_bytes() != data]
    if args.check:
        if stale:
            sys.exit("emit_visual: stale, regenerate with `python3 scripts/emit_visual.py`: " + ", ".join(stale))
        print("emit_visual: up to date")
        return
    for rel, data in outputs.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes(data)
    print(f"emit_visual: wrote {', '.join(sorted(outputs))}")


if __name__ == "__main__":
    main()
