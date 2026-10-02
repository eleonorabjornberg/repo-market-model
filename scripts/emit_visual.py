#!/usr/bin/env python3
"""Emit the visual layer: docs/visual/data/*.json and site/index.html (directive 06).

The descriptive half of the results page: the plumbing, eight years of the
spread, why pressure happens, and what is known at the decision time, plus how
the project was built. Nothing on the page is typed:

* The panel is rebuilt from the tracked fixtures with the repository's own
  `build` command and refused unless its SHA-256 is the published manifest's.
* Every event label and claim about market structure comes from
  `docs/visual/annotations.json`, each with a primary source. `metadata/` is
  read and never written.
* The administered rates in chapter 1 are parsed from a checksummed copy of the
  current FOMC implementation note, never transcribed.
* A placeholder left unfilled is an error, and so is a run record that does
  not declare the as-of information rule (`require_as_of`).
* Days in a locked tier of `metadata/lockbox.json` (`docs/decisions/lockbox.md`)
  are drawn greyed and labelled "held out", and are left out of every count,
  share, median and generated sentence (#141 ruling 3). The tiers are read
  through `repo_model.lockbox`; a tier marked opened is ordinary history.
* The "Start here" block above the chapters is the newcomer layer (#141). Its
  terms come from `docs/visual/glossary.json`, each with a primary source; its
  view N1 holds out the same locked days, through the same reader.
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
import hashlib
import html
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

from repo_model.asof import declared_availability  # noqa: E402
from repo_model.contract import CALENDAR_FEATURES, FEATURE_FIELDS, ON_RRP_DEPLETION_BREAK_BN  # noqa: E402
from repo_model.data import TAX_DEADLINE_MONTHS, corporate_tax_deadline  # noqa: E402
from repo_model.ingest import (  # noqa: E402
    NYFED_ON_RRP_FIELD,
    NYFED_ON_RRP_SOURCE_ID,
    load_snapshot_manifest,
    parse_snapshots,
)
from repo_model.lockbox import locked_tier, locked_tiers  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

FIXTURES = "tests/fixtures/snapshots/funding_inputs"
MANIFEST = "metadata/funding_panel_manifest.json"
SOURCES = "metadata/sources.json"
EVENTS = "metadata/events.json"
THRESHOLDS = "metadata/stress_thresholds.json"
SPLITS = "metadata/evaluation_splits.json"
LOCKBOX = "metadata/lockbox.json"
ANNOTATIONS = "docs/visual/annotations.json"
GLOSSARY = "docs/visual/glossary.json"
MAP = "docs/visual/map.json"
ISSUES = "docs/visual/issues.json"
RUNS = "docs/runs"
SNAPSHOTS = "tests/fixtures/snapshots"
ON_RRP = "tests/fixtures/snapshots/on_rrp_inputs/nyfed_on_rrp"
REPOSITORY = "eleonorabjornberg/repo-market-model"
TEMPLATE = "site/template.html"
PAGE = "site/index.html"
DATA_DIR = "docs/visual/data"

#: What the commit stamp is the latest change to. Every file the script reads
#: directly, the fixtures the panel is built from, and the script itself.
INPUTS = (
    "scripts/emit_visual.py",
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
    FIXTURES,
    MAP,
    ISSUES,
    f":(glob){RUNS}/*.json",
    SNAPSHOTS,
)

#: Run records the model chapters render. Empty until chapters 5 to 7 are built
#: (plan step 6); each one passes `load_run_record`, which fails closed.
MODEL_RECORDS = ()

#: An order-of-magnitude bound on reserve balances in USD billions, the unit the
#: panel carries since #41. Millions land above it, trillions below it.
RESERVE_BILLIONS = (100.0, 100_000.0)

LOCKBOX_RULE = "https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/decisions/lockbox.md"
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
            + ", the project's locked final test period (<a href='" + LOCKBOX_RULE + "'>lockbox rule</a>). "
            "These days are drawn but not coloured, counted or described anywhere on this page.</p>") if held else "",
        "held_out_dots": " Grey dots: held-out days, not counted." if held else "",
        "held_out_footer": (
            " The days " + held_from + " are held out under the "
            "<a href='" + LOCKBOX_RULE + "'>lockbox rule</a>: they are drawn greyed and left out of every count, "
            "median and sentence.") if held else "",
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
        "n1_held_note": (f"Days from {day(spans[0]['start'])} on are held out for the project's final test "
                         f"(<a href='https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/"
                         f"decisions/lockbox.md'>the lockbox rule</a>). They are drawn in grey, labelled "
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


def on_rrp_results(repo):
    """The Desk's ON RRP results, from the tracked snapshots through `ingest`'s own adapter.

    `parse_snapshots` refuses a file whose bytes do not match its manifest's
    SHA-256. A day's result is the latest vintage of it. Returns
    `([(ref_date, available_at, value in USD billions)], {snapshot path: sha256})`,
    the results ordered by when they became public.
    """
    manifests = sorted((repo / ON_RRP).glob("*.json.manifest.json"))
    if not manifests:
        raise VisualError(f"no ON RRP snapshot under {ON_RRP}")
    artifacts = [load_snapshot_manifest(path) for path in manifests]
    latest = {}
    for row in parse_snapshots(artifacts).rows:
        if row.series_id != NYFED_ON_RRP_FIELD:
            continue
        if row.ref_date not in latest or row.available_at > latest[row.ref_date][0]:
            latest[row.ref_date] = (row.available_at, row.value)
    results = sorted(((ref, at, value) for ref, (at, value) in latest.items()), key=lambda o: (o[1], o[0]))
    snapshots = {}
    for path in manifests:
        payload = path.with_name(path.name[:-len(".manifest.json")])
        snapshots[str(payload.relative_to(repo))] = sha256(payload)
    return results, snapshots


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


def map_svg(tag_map, rows, parties):
    """N4's map as a static, accessible <svg>: parties, one arrow per flow, the board under the dealers.

    Each arrow points the way the cash goes and is drawn in its kind's line
    style. An arrow no registered series on the map measures is drawn faint;
    that is derived from the tags' statuses, never typed. Each arrow carries
    its flow's number from the list beside the map.
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
            f'<g class="fl{" faint" if faint else ""}" id="n4f-{key}"><path d="{d}" style="{style}" '
            f'marker-end="url(#n4-head)"/><circle cx="{mx:.1f}" cy="{my:.1f}" r="11"/>'
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
        parts.append(f'<g class="board" id="n4b-{key}"><line x1="{x}" y1="{y + h}" x2="{x}" y2="{top}"/>'
                     f'<rect x="{x - w}" y="{top}" width="{2 * w}" height="34" rx="8"/>'
                     f'<text x="{x}" y="{top + 21}" text-anchor="middle">{html.escape(board["label"])}</text></g>')
        names.append(f"a board of market-wide series under {html.unescape(parties[key])}")
    aria = ("Map of who lends cash to whom. Each arrow points the way the cash goes. "
            + "; ".join(names) + ". The list below the map gives the same flows and their tags.")
    return (f'<svg viewBox="-20 0 800 480" role="img" aria-label="{html.escape(aria)}">'
            '<defs><marker id="n4-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="12" markerHeight="12" markerUnits="userSpaceOnUse" '
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
        return (f"Days from {day(starts[0].isoformat())} on are held out for the project's final test "
                f"(<a href='{LOCKBOX_RULE}'>the lockbox rule</a>) and are never chosen.")
    lock = f"; the project's locked final test period starts on {day(starts[0].isoformat())}" if starts else ""
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
    records = run_record_declarations(repo)
    locked = locked_tiers(repo / LOCKBOX)
    check_annotations(notes)
    check_glossary(glossary)
    for path in MODEL_RECORDS:
        load_run_record(repo / path)
    commit = commit or input_commit(repo)

    with tempfile.TemporaryDirectory() as tmp:
        raw, digest = build_panel(repo, manifest, tmp)
    rows = list(csv.DictReader(raw.decode().splitlines()))
    check_reserve_units(rows)

    decision = time.fromisoformat(manifest["decision_time"])
    n1, n1_fills = newcomer_n1([dict(r) for r in rows], locked, thresholds, notes)
    hist, fills = history(rows, notes, thresholds, regimes, windows, locked)
    fills.update(n1_fills)
    on_rrp, on_rrp_snapshots = on_rrp_results(repo)
    try:
        seg_days = segment_days(rows, locked, on_rrp, registry, decision)
    except ValueError as exc:
        raise VisualError(f"N4's segment chart: {exc}") from exc
    n4, n4_fills = newcomer_n4(tag_map, registry, manifest, records, snapshot, tracked_snapshots(repo), notes,
                               glossary, rows, seg_days, decision, locked)
    fills.update(n4_fills)
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
    })

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
    payloads = {"history": hist, "plumbing": plumbing, "clock": clock_data, "build": build, "newcomer_n1": n1,
                "newcomer_n4": n4}
    n4_provenance = dict(provenance, inputs=dict(
        {rel: sha256(repo / rel) for rel in (MAP, ISSUES, SOURCES, MANIFEST, ANNOTATIONS, GLOSSARY)},
        **{rel: sha256(repo / rel) for rel in records}, **on_rrp_snapshots))
    out = {}
    for name, payload in payloads.items():
        doc = {"provenance": n4_provenance if name == "newcomer_n4" else provenance, "data": payload}
        out[f"{DATA_DIR}/{name}.json"] = (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                                      ensure_ascii=False) + "\n").encode("utf-8")
    page_data = {k: payloads[k] for k in ("history", "plumbing", "clock", "newcomer_n1")}
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
